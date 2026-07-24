from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import ProductVariant

from .cart import Cart
from .forms import CheckoutForm, PaymentProofForm
from .models import BankAccount, Order, OrderEvent, OrderItem


def _is_ajax(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart_detail.html", {"cart": cart})


@require_POST
def cart_add(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if variant.is_out_of_stock:
        error = f"Sorry, {variant.product.name} ({variant.size.label}) is out of stock."
        if _is_ajax(request):
            return JsonResponse({"success": False, "message": error}, status=400)
        messages.error(request, error)
        return redirect(variant.product.get_absolute_url())

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    cart.add(variant=variant, quantity=quantity)
    success_message = f"Added {variant.product.name} ({variant.size.label}) to your bag."

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "message": success_message,
            "cart_count": len(cart),
            "cart_subtotal": str(cart.subtotal),
        })

    messages.success(request, success_message)
    return redirect("orders:cart_detail")


@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity <= 0:
        cart.remove(variant_id)
        line_total = "0"
    else:
        cart.add(variant=variant, quantity=quantity, replace=True)
        line_total = str(variant.effective_price * quantity)

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "cart_count": len(cart),
            "cart_subtotal": str(cart.subtotal),
            "line_total": line_total,
            "removed": quantity <= 0,
        })
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, variant_id):
    cart = Cart(request)
    cart.remove(variant_id)

    if _is_ajax(request):
        return JsonResponse({
            "success": True,
            "cart_count": len(cart),
            "cart_subtotal": str(cart.subtotal),
        })

    messages.info(request, "Item removed from your bag.")
    return redirect("orders:cart_detail")


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your bag is empty — add something before checking out.")
        return redirect("catalog:shop")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Re-validate stock inside the transaction to avoid overselling.
                cart_items = list(cart)
                for entry in cart_items:
                    variant = ProductVariant.objects.select_for_update().get(id=entry["variant"].id)
                    if variant.stock_quantity < entry["quantity"]:
                        messages.error(
                            request,
                            f"Sorry, only {variant.stock_quantity} left of "
                            f"{variant.product.name} ({variant.size.label}). Please update your bag.",
                        )
                        return redirect("orders:cart_detail")

                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.customer = request.user
                order.shipping_fee = order.shipping_zone.fee
                order.bank_account = BankAccount.objects.filter(is_active=True).first()
                order.save()

                for entry in cart_items:
                    variant = ProductVariant.objects.select_for_update().get(id=entry["variant"].id)
                    OrderItem.objects.create(
                        order=order,
                        product_variant=variant,
                        product_name=variant.product.name,
                        size_label=variant.size.label,
                        quantity=entry["quantity"],
                        unit_price=entry["unit_price"],
                    )
                    variant.stock_quantity -= entry["quantity"]
                    variant.save(update_fields=["stock_quantity"])

                order.recalculate_totals()
                order.log_event("Order placed.", event_type=OrderEvent.EventType.CREATED)
                cart.clear()

            return redirect("orders:order_success", order_number=order.order_number)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {"full_name": request.user.get_full_name(), "email": request.user.email}
        form = CheckoutForm(initial=initial)

    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    proof_form = PaymentProofForm()
    return render(request, "orders/order_success.html", {"order": order, "proof_form": proof_form})


@require_POST
def upload_payment_proof(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if hasattr(order, "payment_proof"):
        messages.info(request, "You've already uploaded proof of payment for this order. Our team will review it shortly.")
        return redirect("orders:order_success", order_number=order.order_number)

    form = PaymentProofForm(request.POST, request.FILES)
    if form.is_valid():
        proof = form.save(commit=False)
        proof.order = order
        proof.save()
        order.status = Order.Status.PROOF_SUBMITTED
        order.save(update_fields=["status"])
        order.log_event("Payment proof uploaded by customer.", event_type=OrderEvent.EventType.PROOF_UPLOADED)
        messages.success(request, "Thanks! We've received your payment proof and will confirm your order shortly.")
    else:
        messages.error(request, "There was a problem with your upload — please try again.")
    return redirect("orders:order_success", order_number=order.order_number)


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related("shipping_zone", "bank_account").prefetch_related(
            "items", "events", "refunds",
        ),
        order_number=order_number, customer=request.user,
    )
    proof_form = None if hasattr(order, "payment_proof") else PaymentProofForm()
    return render(request, "orders/order_detail.html", {
        "order": order,
        "timeline": order.events.filter(visible_to_customer=True),
        "refunds": order.refunds.all(),
        "proof_form": proof_form,
        "can_cancel": order.status in Order.CUSTOMER_CANCELLABLE_STATUSES,
    })


@login_required
@require_POST
def order_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    if order.status not in Order.CUSTOMER_CANCELLABLE_STATUSES:
        messages.error(request, "This order can no longer be cancelled — it's already being processed. Contact us if you need help.")
    else:
        order.cancel(actor=request.user)
        messages.success(request, f"Order {order.order_number} has been cancelled.")
    return redirect("orders:order_detail", order_number=order.order_number)


@login_required
@require_POST
def order_reorder(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items__product_variant"), order_number=order_number, customer=request.user)
    cart = Cart(request)
    added, unavailable = 0, []
    for item in order.items.all():
        variant = item.product_variant
        if variant.is_out_of_stock:
            unavailable.append(f"{item.product_name} ({item.size_label})")
            continue
        cart.add(variant=variant, quantity=min(item.quantity, variant.stock_quantity))
        added += 1

    if added:
        messages.success(request, f"Added {added} item(s) from this order back to your bag.")
    if unavailable:
        messages.warning(request, "Out of stock and skipped: " + ", ".join(unavailable))
    if not added and not unavailable:
        messages.info(request, "This order has no items to reorder.")
    return redirect("orders:cart_detail")


def track_order(request):
    order = None
    searched = False
    if request.method == "POST":
        searched = True
        order_number = request.POST.get("order_number", "").strip()
        email = request.POST.get("email", "").strip()
        order = Order.objects.filter(order_number__iexact=order_number, email__iexact=email).first()
        if not order:
            messages.error(request, "We couldn't find an order with those details. Please double-check and try again.")
    return render(request, "orders/track_order.html", {"order": order, "searched": searched})
