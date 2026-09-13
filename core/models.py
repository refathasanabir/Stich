from django.db import models
from django.contrib.auth.models import User


class Design(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True, null=True
    )  # <--- Added blank=True, null=True
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="designs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("Customer", "Customer"),
        ("Tailor", "Tailor"),
        ("Rider", "Rider"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default="Customer")

    # Role-specific fields
    shop_name = models.CharField(max_length=255, blank=True, null=True)  # For Tailors
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)  # For Riders
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
