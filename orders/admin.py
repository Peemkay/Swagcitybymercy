from django.contrib import admin
from django.utils.html import format_html

from .models import BankAccount, Order, OrderEvent, OrderItem, PaymentProof, Refund, ShippingZone


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "delivery_estimate", "fee", "is_active", "order")
    list_editable = ("fee", "is_active", "order")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_name", "account_number", "is_active", "order")
    list_editable = ("is_active", "order")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_variant", "product_name", "size_label", "quantity", "unit_price", "line_total")
    can_delete = False

    def line_total(self, obj):
        return obj.line_total if obj.line_total is not None else "—"


class PaymentProofInline(admin.StackedInline):
    model = PaymentProof
    extra = 0
    readonly_fields = ("uploaded_at", "proof_preview")
    fields = ("proof_preview", "amount_paid", "note", "uploaded_at")

    def proof_preview(self, obj):
        if obj and obj.image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height:220px;" /></a>', obj.image.url)
        return "No proof uploaded yet"
    proof_preview.short_description = "Payment screenshot"


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 1
    fields = ("amount", "reason", "status", "processed_by", "created_at")
    readonly_fields = ("created_at",)


class OrderEventInline(admin.TabularInline):
    model = OrderEvent
    extra = 0
    fields = ("created_at", "event_type", "message", "actor", "visible_to_customer")
    readonly_fields = ("created_at", "event_type", "message", "actor", "visible_to_customer")
    can_delete = False
    verbose_name_plural = "Activity timeline"

    def has_add_permission(self, request, obj=None):
        return False


STATUS_COLORS = {
    "pending_payment": "#95a5a6",
    "proof_submitted": "#f39c12",
    "payment_confirmed": "#27ae60",
    "processing": "#2980b9",
    "shipped": "#8e44ad",
    "delivered": "#16a085",
    "cancelled": "#c0392b",
    "refunded": "#7f8c8d",
}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number", "full_name", "phone", "shipping_zone", "total",
        "status_badge", "has_proof", "created_at",
    )
    list_filter = ("status", "shipping_zone", "created_at")
    search_fields = ("order_number", "full_name", "email", "phone")
    readonly_fields = ("order_number", "subtotal", "total", "created_at", "updated_at")
    inlines = [OrderItemInline, PaymentProofInline, RefundInline, OrderEventInline]
    actions = ["mark_payment_confirmed", "mark_processing", "mark_shipped", "mark_delivered", "mark_cancelled"]

    fieldsets = (
        ("Order", {"fields": ("order_number", "status", "created_at", "updated_at")}),
        ("Customer", {"fields": ("customer", "full_name", "email", "phone")}),
        ("Delivery", {"fields": ("address", "city", "state", "country", "shipping_zone")}),
        ("Payment", {"fields": ("bank_account", "subtotal", "shipping_fee", "total")}),
        ("Notes", {"fields": ("customer_notes", "admin_notes")}),
    )

    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, "#333")
        return format_html('<b style="color:{}">{}</b>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    def has_proof(self, obj):
        return hasattr(obj, "payment_proof")
    has_proof.boolean = True
    has_proof.short_description = "Proof?"

    def save_formset(self, request, form, formset, change):
        if formset.model is Refund:
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            for obj in instances:
                if not obj.pk and not obj.processed_by_id:
                    obj.processed_by = request.user
                obj.save()
            formset.save_m2m()
        else:
            formset.save()

    def _apply_status(self, request, queryset, status, message):
        for order in queryset.exclude(status=status):
            order.status = status
            order.save(update_fields=["status"])
            order.log_event(message, event_type=OrderEvent.EventType.STATUS_CHANGE, actor=request.user)
            order.notify_customer(f"Order {order.order_number}: {message}", link=order.get_absolute_url())

    @admin.action(description="Mark selected orders as Payment confirmed")
    def mark_payment_confirmed(self, request, queryset):
        self._apply_status(request, queryset, Order.Status.PAYMENT_CONFIRMED, "Payment confirmed — we're getting your order ready.")

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        self._apply_status(request, queryset, Order.Status.PROCESSING, "Your order is being processed.")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        self._apply_status(request, queryset, Order.Status.SHIPPED, "Your order has shipped!")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        self._apply_status(request, queryset, Order.Status.DELIVERED, "Your order was marked as delivered.")

    @admin.action(description="Cancel selected orders and restock items")
    def mark_cancelled(self, request, queryset):
        for order in queryset.exclude(status=Order.Status.CANCELLED):
            order.cancel(actor=request.user)


@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):
    """Read-only, cross-order activity log — 'what happened, on which order, and who did it'."""
    list_display = ("created_at", "order", "event_type", "message", "actor", "visible_to_customer")
    list_filter = ("event_type", "visible_to_customer", "created_at")
    search_fields = ("order__order_number", "message")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "processed_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number", "reason")
    autocomplete_fields = ("order",)

    def save_model(self, request, obj, form, change):
        if not obj.processed_by_id:
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)
