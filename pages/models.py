from django.db import models


class SiteSettings(models.Model):
    """Singleton model — admin edits store-wide info shown across the site."""
    site_name = models.CharField(max_length=100, default="Swagcitybymercy")
    tagline = models.CharField(max_length=255, blank=True, default="Quality, luxury female apparel — Lagos, Nigeria.")
    about_text = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True, help_text="Digits only with country code, e.g. 2348012345678")
    instagram_handle = models.CharField(max_length=100, blank=True, default="swagcitybymercy")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    lagos_delivery_note = models.CharField(max_length=255, blank=True, default="1-2 working days within Lagos")
    other_regions_delivery_note = models.CharField(max_length=255, blank=True, default="5-7 working days for other regions in Nigeria")
    international_delivery_note = models.CharField(max_length=255, blank=True, default="5-6 working days for international orders")

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.created_at:%Y-%m-%d}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
