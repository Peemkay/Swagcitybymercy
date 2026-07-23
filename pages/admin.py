from django.contrib import admin

from .models import ContactMessage, NewsletterSubscriber, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Store identity", {"fields": ("site_name", "tagline", "about_text", "logo")}),
        ("Contact & socials", {"fields": ("whatsapp_number", "instagram_handle", "contact_email", "contact_phone")}),
        ("Delivery notes (shown at checkout)", {
            "fields": ("lagos_delivery_note", "other_regions_delivery_note", "international_delivery_note"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_filter = ("is_read",)
    list_editable = ("is_read",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)
