from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("customer/", include("customers.urls")),
    path("measurements/", include("measurements.urls")),
]
