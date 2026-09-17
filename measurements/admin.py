from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "chest",
        "waist",
        "shoulders",
        "sleeve_length",
        "created_at",
    )
    search_fields = ("profile__name",)
