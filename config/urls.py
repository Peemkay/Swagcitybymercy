from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.urls import include, path, reverse


def admin_login_default_next(request):
    """A direct GET to /admin/login/ has no ?next= — Django's LoginView then
    falls back to the project-wide LOGIN_REDIRECT_URL, which points at the
    *customer* account dashboard. The normal @staff_member_required flow
    (visiting /admin/ while logged out) always appends ?next= itself and is
    unaffected; this only covers someone landing on /admin/login/ directly,
    forcing them back into /admin/ afterwards instead of the storefront.
    """
    if request.method == "GET" and "next" not in request.GET:
        params = request.GET.copy()
        params["next"] = reverse("admin:index")
        return HttpResponseRedirect(f"{request.path}?{params.urlencode()}")
    return admin.site.login(request)


urlpatterns = [
    path("admin/dashboard/", include("pages.admin_urls")),
    # Overrides admin:login / admin:logout's redirect targets specifically —
    # the project-wide LOGIN_REDIRECT_URL / LOGOUT_REDIRECT_URL point at the
    # customer storefront, which would otherwise dump staff in and out of
    # the wrong place. Same path as Django's own admin:login/admin:logout,
    # so {% url %} lookups by name still resolve correctly either way.
    path("admin/login/", admin_login_default_next, name="admin_login_override"),
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
