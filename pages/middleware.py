from django.conf import settings


class SyncJazzminBrandingMiddleware:
    """Keeps the admin theme's text branding in sync with the SiteSettings
    singleton, so store owners only ever edit branding in one place.

    Jazzmin re-reads django.conf.settings.JAZZMIN_SETTINGS fresh on every
    request (see jazzmin.settings.get_settings), so mutating the dict here
    is picked up immediately with no server restart needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            from .models import SiteSettings

            site = SiteSettings.load()
            jazzmin_settings = settings.JAZZMIN_SETTINGS
            jazzmin_settings["site_title"] = f"{site.site_name} Admin"
            jazzmin_settings["site_header"] = site.site_name
            jazzmin_settings["site_brand"] = site.site_name
            jazzmin_settings["copyright"] = site.site_name
            if site.tagline:
                jazzmin_settings["welcome_sign"] = site.tagline

        return self.get_response(request)
