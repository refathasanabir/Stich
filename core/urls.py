from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("gallery/", views.gallery_view, name="gallery"),  # Public Guest Gallery
    path(
        "marketplace/", views.marketplace_gallery_view, name="marketplace"
    ),  # Customer Marketplace page
    path(
        "marketplace/item/<int:pk>/",
        views.marketplace_detail_view,
        name="marketplace_detail",
    ),
    path("pricing/", views.pricing, name="pricing"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("tailors/", views.tailor_list, name="tailor_list"),
    path("tailors/details/", views.tailor_details, name="tailor_details"),
    path("logout/", views.logout_view, name="logout"),
]
