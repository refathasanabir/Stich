from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profiles/", views.profiles, name="profiles"),
    path("orders/", views.customer_orders, name="orders"),
    # Cart Routes
    path("cart/", views.customer_cart, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.customer_checkout, name="checkout"),
    # Direct Checkout & Success Routes
    path(
        "checkout/direct/<int:design_id>/",
        views.direct_checkout,
        name="direct_checkout",
    ),
    path("order-success/<str:order_id>/", views.order_success, name="order_success"),
    # Misc Routes
    path("notifications/", views.customer_notifications, name="notifications"),
    path("settings/", views.customer_settings, name="settings"),
    path("chat/", views.customer_chat, name="chat"),
    path("checkout/<int:design_id>/", views.checkout, name="checkout"),
]
