from django.contrib import admin
from django.contrib.admin.models import LogEntry

from .models import ContactMessage, FAQItem, NewsletterSubscriber, PolicyPage, SiteSettings


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


@admin.register(PolicyPage)
class PolicyPageAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Fixed set of kinds seeded by migration — edit them, don't add more.
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Read-only view over Django's own admin action audit trail — every
    add/change/delete made anywhere in the admin, by whom and when."""
    list_display = ("action_time", "user", "content_type", "object_repr", "action_flag_display", "change_message")
    list_filter = ("action_flag", "content_type", "user")
    search_fields = ("object_repr", "change_message")
    date_hierarchy = "action_time"

    def action_flag_display(self, obj):
        return {1: "Added", 2: "Changed", 3: "Deleted"}.get(obj.action_flag, obj.action_flag)
    action_flag_display.short_description = "Action"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
