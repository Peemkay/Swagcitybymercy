"""
Django settings for the Swagcitybymercy e-commerce project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------
# In production, set these as real environment variables (see README.md).
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-xyoa3z@htr+ls=y1!_g6-a8_geh7vyaj62h-dp^uf#zxdyj(%@",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # must be listed before django.contrib.admin to override its templates
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # local apps
    "accounts",
    "catalog",
    "orders",
    "pages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "orders.context_processors.cart_summary",
                "pages.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Defaults to SQLite for easy local/demo use. For production, set DATABASE_URL
# style env vars or point this at Postgres/MySQL (see README.md).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:dashboard"
LOGOUT_REDIRECT_URL = "pages:home"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

if not DEBUG:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        # Not the Manifest variant: django-jazzmin's own admin/base.html contains
        # a {% static 'vendor/bootswatch' %} reference to a bare directory (used
        # as a JS data attribute, not a real file). ManifestStaticFilesStorage
        # requires every {% static %} tag to resolve to an actual collected file
        # and raises a hard 500 otherwise — harmless under the plain storage
        # below, which just emits the (unused) URL without validating it.
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Site-specific settings
# ---------------------------------------------------------------------------
SITE_NAME = "Swagcitybymercy"

# Naira formatting helper used across templates/views
CURRENCY_SYMBOL = "\u20a6"  # Naira sign

# ---------------------------------------------------------------------------
# Security hardening (auto-enabled when DEBUG is off)
# ---------------------------------------------------------------------------
if not DEBUG:
    # Behind a TLS-terminating proxy (PythonAnywhere, Nginx, etc.) Django must
    # be told requests arriving as HTTP were originally HTTPS, or SECURE_SSL_REDIRECT
    # loops forever and secure cookies never stick.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "True") == "True"
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

MAX_UPLOAD_SIZE_MB = 5  # for payment proof screenshots

# ---------------------------------------------------------------------------
# Admin theme (django-jazzmin) — mirrors the storefront's black/blush/gold identity
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Swagcitybymercy Admin",
    "site_header": "Swagcitybymercy",
    "site_brand": "Swagcitybymercy",
    "site_logo": None,
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "Welcome back — here's what's happening in your store.",
    "copyright": "Swagcitybymercy",
    "search_model": ["catalog.Product", "orders.Order"],
    "user_avatar": None,

    "topmenu_links": [
        {"name": "Dashboard", "url": "admin_dashboard:index", "permissions": ["auth.view_user"]},
        {"name": "View Store", "url": "pages:home", "new_window": True},
        {"model": "auth.User"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "orders", "orders.Order", "catalog", "catalog.Product", "catalog.Category",
        "pages", "accounts",
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "catalog.Category": "fas fa-tags",
        "catalog.Size": "fas fa-ruler",
        "catalog.Product": "fas fa-tshirt",
        "catalog.ProductVariant": "fas fa-boxes-stacked",
        "orders.Order": "fas fa-receipt",
        "orders.ShippingZone": "fas fa-truck",
        "orders.BankAccount": "fas fa-building-columns",
        "accounts.CustomerProfile": "fas fa-address-card",
        "pages.SiteSettings": "fas fa-sliders-h",
        "pages.ContactMessage": "fas fa-envelope-open-text",
        "pages.NewsletterSubscriber": "fas fa-paper-plane",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    "related_modal_active": True,
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    "show_ui_builder": False,

    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
    "actions_sticky_top": True,
}
