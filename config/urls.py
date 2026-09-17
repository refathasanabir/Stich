from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", include("adminpanel.urls")),
    path("", include("core.urls")),
    path("customer/", include("customers.urls")),
    path("measurements/", include("measurements.urls")),
    path("tailor/", include("tailors.urls")),
    # path("rider/", include("riders.urls")), # Uncomment if you have a riders app
    path("rider/", include("riders.urls")),
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="customers/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="customers/password_change_done.html"
        ),
        name="password_change_done",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
