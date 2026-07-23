from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

urlpatterns = [
    path("admin/dashboard/", include("pages.admin_urls")),
    # Overrides admin:logout's target specifically — the project-wide
    # LOGOUT_REDIRECT_URL points customer logouts at the storefront home,
    # which would otherwise dump a staff member out of the admin entirely.
    path("admin/logout/", LogoutView.as_view(next_page="admin:login"), name="admin_logout_override"),
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("shop/", include("catalog.urls")),
    path("orders/", include("orders.urls")),
    path("account/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
