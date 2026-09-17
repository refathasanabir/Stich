from django.db import models
from customers.models import MeasurementProfile


class Measurement(models.Model):
    profile = models.OneToOneField(
        MeasurementProfile, on_delete=models.CASCADE, related_name="measurements"
    )
    chest = models.DecimalField(max_digits=5, decimal_places=2, help_text="Inches")
    waist = models.DecimalField(max_digits=5, decimal_places=2, help_text="Inches")
    shoulders = models.DecimalField(max_digits=5, decimal_places=2, help_text="Inches")
    sleeve_length = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Inches"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Measurements for {self.profile.name}"
