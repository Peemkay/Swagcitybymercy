from django.contrib import admin
from django.utils.html import format_html

from .models import BankAccount, Order, OrderItem, PaymentProof, ShippingZone


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


STATUS_COLORS = {
    "pending_payment": "#95a5a6",
    "proof_submitted": "#f39c12",
    "payment_confirmed": "#27ae60",
    "processing": "#2980b9",
    "shipped": "#8e44ad",
    "delivered": "#16a085",
    "cancelled": "#c0392b",
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
    inlines = [OrderItemInline, PaymentProofInline]
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

    @admin.action(description="Mark selected orders as Payment confirmed")
    def mark_payment_confirmed(self, request, queryset):
        queryset.update(status=Order.Status.PAYMENT_CONFIRMED)

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status=Order.Status.PROCESSING)

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)

    @admin.action(description="Cancel selected orders and restock items")
    def mark_cancelled(self, request, queryset):
        for order in queryset.exclude(status=Order.Status.CANCELLED):
            for item in order.items.all():
                variant = item.product_variant
                variant.stock_quantity += item.quantity
                variant.save(update_fields=["stock_quantity"])
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])
