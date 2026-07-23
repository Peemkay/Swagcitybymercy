from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from catalog.models import ProductVariant
from orders.models import Order

from .models import ContactMessage


REVENUE_STATUSES = [
    Order.Status.PAYMENT_CONFIRMED,
    Order.Status.PROCESSING,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
]


@staff_member_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    month_start = today.replace(day=1)
    week_start = today - timedelta(days=7)

    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_this_week = Order.objects.filter(created_at__date__gte=week_start).count()
    awaiting_action = Order.objects.filter(
        status__in=[Order.Status.PENDING_PAYMENT, Order.Status.PROOF_SUBMITTED],
    ).count()

    revenue_month = Order.objects.filter(
        status__in=REVENUE_STATUSES, created_at__date__gte=month_start,
    ).aggregate(total=Sum("total"))["total"] or 0

    low_stock_variants = ProductVariant.objects.select_related("product", "size").filter(
        stock_quantity__gt=0, stock_quantity__lte=3,
    ).order_by("stock_quantity")[:8]
    out_of_stock_count = ProductVariant.objects.filter(stock_quantity=0).count()

    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    recent_orders = Order.objects.select_related("shipping_zone").order_by("-created_at")[:8]

    context = admin.site.each_context(request)
    context.update({
        "title": "Dashboard",
        "orders_today": orders_today,
        "orders_this_week": orders_this_week,
        "awaiting_action": awaiting_action,
        "revenue_month": revenue_month,
        "low_stock_variants": low_stock_variants,
        "out_of_stock_count": out_of_stock_count,
        "unread_messages": unread_messages,
        "recent_orders": recent_orders,
    })
    return render(request, "admin/dashboard.html", context)
