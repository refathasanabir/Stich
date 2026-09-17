from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profiles/", views.profiles, name="profiles"),
    path("orders/", views.customer_orders, name="orders"),
    path("cart/", views.customer_cart, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.customer_checkout, name="checkout"),
    path("notifications/", views.customer_notifications, name="notifications"),
    path("settings/", views.customer_settings, name="settings"),
    path("chat/", views.customer_chat, name="chat"),
]
