from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, blank=True)
    default_address = models.CharField(max_length=255, blank=True)
    default_city = models.CharField(max_length=100, blank=True)
    default_state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile for {self.user}"


class Notification(models.Model):
    """In-app notifications for a customer's account — e.g. order status
    changes and refunds. Guest checkouts have no account to notify; they
    rely on the public order-tracking page instead."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
