from django.db import models


class SiteSettings(models.Model):
    """Singleton model — admin edits store-wide info shown across the site."""
    site_name = models.CharField(max_length=100, default="Swagcitybymercy")
    tagline = models.CharField(
        max_length=255, blank=True, default="Quality, luxury female apparel — Lagos, Nigeria.",
        help_text="Short slogan/motto shown in the header area, browser tab, and search results.",
    )
    about_text = models.TextField(blank=True, help_text="Longer site description, shown on the About page and homepage.")
    logo = models.ImageField(
        upload_to="site/", blank=True, null=True,
        help_text="Shown in the site header, footer, and browser tab icon. Square images work best.",
    )
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


class PolicyPage(models.Model):
    class Kind(models.TextChoices):
        RETURNS = "returns", "Return & Refund Policy"
        PRIVACY = "privacy", "Privacy Policy"
        TERMS = "terms", "Terms & Conditions"

    kind = models.CharField(max_length=20, choices=Kind.choices, unique=True)
    title = models.CharField(max_length=150)
    content = models.TextField(help_text="Supports basic HTML (paragraphs, lists, bold, links).")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("pages:policy", args=[self.kind])


class FAQItem(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ item"

    def __str__(self):
        return self.question


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email
