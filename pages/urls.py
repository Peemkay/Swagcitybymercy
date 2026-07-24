from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("returns-policy/", views.policy_page, {"kind": "returns"}, name="returns_policy"),
    path("privacy-policy/", views.policy_page, {"kind": "privacy"}, name="privacy_policy"),
    path("terms-conditions/", views.policy_page, {"kind": "terms"}, name="terms_conditions"),
    path("policy/<str:kind>/", views.policy_page, name="policy"),
    path("faq/", views.faq, name="faq"),
]
