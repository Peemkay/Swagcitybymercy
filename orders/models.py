import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

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

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SCM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.shipping_fee
        self.save(update_fields=["subtotal", "total"])


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
