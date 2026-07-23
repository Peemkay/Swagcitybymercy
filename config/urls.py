from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/dashboard/", include("pages.admin_urls")),
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("shop/", include("catalog.urls")),
    path("orders/", include("orders.urls")),
    path("account/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
