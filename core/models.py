from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("Customer", "Customer"),
        ("Tailor", "Tailor"),
        ("Rider", "Rider"),
        ("Admin", "Admin"),
    )
    STATUS_CHOICES = (
        ("Pending Approval", "Pending Approval"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default="Customer")
    approval_status = models.CharField(
        choices=STATUS_CHOICES, max_length=20, default="Pending Approval"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Rider specific (Shop specific fields will move to the tailors app)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.approval_status})"


class Design(models.Model):
    CATEGORY_CHOICES = [
        ("Panjabi", "Panjabi"),
        ("Shirt", "Shirt"),
        ("Blouse", "Blouse"),
        ("Suit", "Suit"),
    ]
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Unisex", "Unisex")]

    # Link the design to the tailor shop
    shop = models.ForeignKey(
        "tailors.TailorShop",
        on_delete=models.CASCADE,
        related_name="designs",
        null=True,
    )
    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="Shirt"
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Male")
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    image = models.ImageField(upload_to="designs/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.shop}"
