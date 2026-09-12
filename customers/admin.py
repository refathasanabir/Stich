from django.contrib import admin
from .models import (
    GlobalMeasurementField,
    MeasurementProfile,
    Order,
    DesignCustomizationOption,
)


@admin.register(GlobalMeasurementField)
class GlobalMeasurementFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(DesignCustomizationOption)
class DesignCustomizationAdmin(admin.ModelAdmin):
    list_display = ("product_name", "shop_name")
    filter_horizontal = (
        "required_fields",
    )  # Gives your friend a clean multi-select box UI


admin.site.register(MeasurementProfile)
admin.site.register(Order)
