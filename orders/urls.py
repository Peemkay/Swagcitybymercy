from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:variant_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:variant_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:variant_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<str:order_number>/", views.order_success, name="order_success"),
    path("success/<str:order_number>/upload-proof/", views.upload_payment_proof, name="upload_payment_proof"),
    path("track/", views.track_order, name="track_order"),
]
