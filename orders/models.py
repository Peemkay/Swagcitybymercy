import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from catalog.models import ProductVariant


class ShippingZone(models.Model):
    """Delivery regions the admin can price and edit — e.g. Lagos, Other Nigeria, International."""
    name = models.CharField(max_length=100, unique=True)
    delivery_estimate = models.CharField(
        max_length=100, help_text="Shown to customers, e.g. '1-2 working days'.",
    )
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Shipping zones"

    def __str__(self):
        return f"{self.name} ({self.delivery_estimate})"


class BankAccount(models.Model):
    """Company bank account(s) shown to customers at checkout for manual transfer."""
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "bank_name"]

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PROOF_SUBMITTED = "proof_submitted", "Payment proof submitted"
        PAYMENT_CONFIRMED = "payment_confirmed", "Payment confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    # A customer can only self-cancel before the store has started acting on
    # the order (i.e. before payment is confirmed and processing begins).
    CUSTOMER_CANCELLABLE_STATUSES = (Status.PENDING_PAYMENT, Status.PROOF_SUBMITTED)

    order_number = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True,
    )

    # Contact / shipping details (kept on the order so guest checkout works too)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Nigeria")
    shipping_zone = models.ForeignKey(ShippingZone, on_delete=models.PROTECT, related_name="orders")

    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders_paid_here",
        help_text="Bank account the customer was asked to pay into.",
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT)
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes, not visible to the customer.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[self.order_number])

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SCM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.shipping_fee
        self.save(update_fields=["subtotal", "total"])

    def log_event(self, message, event_type=None, actor=None, visible_to_customer=True):
        """Record a timeline entry — the backbone of both the customer-facing
        order timeline and the admin's cross-order activity log."""
        event = self.events.create(
            event_type=event_type or OrderEvent.EventType.NOTE,
            message=message,
            actor=actor,
            visible_to_customer=visible_to_customer,
        )
        return event

    def notify_customer(self, message, link=""):
        """Create an in-app notification for the account this order belongs
        to. Guest checkouts (no linked account) have nothing to notify —
        they rely on the public order-tracking page instead."""
        if not self.customer_id:
            return None
        from accounts.models import Notification
        return Notification.objects.create(user=self.customer, message=message, link=link)

    def cancel(self, actor=None, reason=""):
        """Cancel the order, restock its items, and record the event —
        shared by the admin bulk action and the customer self-service view
        so both paths stay in sync."""
        if self.status == self.Status.CANCELLED:
            return
        for item in self.items.select_related("product_variant"):
            variant = item.product_variant
            variant.stock_quantity += item.quantity
            variant.save(update_fields=["stock_quantity"])
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
        who = "You" if actor is None else actor.get_full_name() or actor.username
        message = f"Order cancelled by {who}." + (f" Reason: {reason}" if reason else "")
        self.log_event(message, event_type=OrderEvent.EventType.STATUS_CHANGE, actor=actor)
        self.notify_customer(
            f"Your order {self.order_number} has been cancelled.",
            link=self.get_absolute_url(),
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_variant = models.ForeignKey(
        ProductVariant, related_name="order_items", on_delete=models.PROTECT,
    )
    product_name = models.CharField(max_length=200, help_text="Snapshot of the product name at time of order.")
    size_label = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def line_total(self):
        if self.unit_price is None or self.quantity is None:
            return None
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name} ({self.size_label})"


def payment_proof_path(instance, filename):
    return f"payment_proofs/{instance.order.order_number}/{filename}"


class PaymentProof(models.Model):
    order = models.OneToOneField(Order, related_name="payment_proof", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=payment_proof_path)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proof for {self.order.order_number}"


class OrderEvent(models.Model):
    """One entry in an order's timeline — powers both the customer-facing
    order status history and the admin's cross-order activity log."""

    class EventType(models.TextChoices):
        CREATED = "created", "Order placed"
        STATUS_CHANGE = "status_change", "Status change"
        PROOF_UPLOADED = "proof_uploaded", "Payment proof uploaded"
        REFUND = "refund", "Refund"
        NOTE = "note", "Note"

    order = models.ForeignKey(Order, related_name="events", on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.NOTE)
    message = models.CharField(max_length=255)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Staff member who triggered this — blank for customer/system actions.",
    )
    visible_to_customer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_number}: {self.message}"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    order = models.ForeignKey(Order, related_name="refunds", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField(blank=True, help_text="Why the refund is being issued — shown to the customer.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="refunds_processed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund of {self.amount} for {self.order.order_number}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous_status = Refund.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        super().save(*args, **kwargs)

        detail_url = self.order.get_absolute_url()
        if is_new:
            reason_suffix = f" Reason: {self.reason}" if self.reason else ""
            if self.status == Refund.Status.COMPLETED:
                # Covers an admin entering a refund that's already been paid out
                # (e.g. bank transfer done before logging it), skipping "pending".
                self.order.log_event(
                    f"Refund of ₦{self.amount:,.0f} completed.{reason_suffix}",
                    event_type=OrderEvent.EventType.REFUND, actor=self.processed_by,
                )
                self.order.notify_customer(
                    f"Your refund of ₦{self.amount:,.0f} for order {self.order.order_number} has been completed.",
                    link=detail_url,
                )
            else:
                self.order.log_event(
                    f"Refund of ₦{self.amount:,.0f} initiated.{reason_suffix}",
                    event_type=OrderEvent.EventType.REFUND, actor=self.processed_by,
                )
                self.order.notify_customer(
                    f"A refund of ₦{self.amount:,.0f} has been initiated for order {self.order.order_number}.",
                    link=detail_url,
                )
        elif previous_status != self.status:
            self.order.log_event(
                f"Refund status changed to {self.get_status_display()}.",
                event_type=OrderEvent.EventType.REFUND, actor=self.processed_by,
            )
            if self.status == Refund.Status.COMPLETED:
                self.order.notify_customer(
                    f"Your refund of ₦{self.amount:,.0f} for order {self.order.order_number} has been completed.",
                    link=detail_url,
                )
