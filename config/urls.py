from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", include("adminpanel.urls")),
    path("", include("core.urls")),
    path("customer/", include("customers.urls")),
    path("measurements/", include("measurements.urls")),
    path("tailor/", include("tailors.urls")),
    # path("rider/", include("riders.urls")), # Uncomment if you have a riders app
    path("rider/", include("riders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
