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
