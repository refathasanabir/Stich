from django.db import models
from django.contrib.auth.models import User


class GlobalMeasurementField(models.Model):
    """Admin manages master fields like Shoulder, Collar, Inseam, Bust, etc."""

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MeasurementProfile(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Unisex", "Unisex")]
    RELATION_CHOICES = [("Self", "Myself"), ("Family", "Family Member")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default="Self")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    category = models.CharField(max_length=50)  # e.g., "Panjabi", "Suit", "Blouse"

    # MySQL 8+ handles JSON natively. This matches Record<string, string> from Figma perfectly.
    values = models.JSONField(
        default=dict,
        blank=True,
        help_text='Stores measurements dynamically, e.g. {"Chest": "40", "Shoulder": "18"}',
    )

    is_default = models.BooleanField(default=False)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class DesignCustomizationOption(models.Model):
    """Shop Owners link their specific products to required measurement fields"""

    product_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    required_fields = models.ManyToManyField(GlobalMeasurementField)

    def __str__(self):
        return f"{self.product_name} ({self.shop_name})"


class CartItem(models.Model):
    """Tracks items added to a customer's shopping cart before checkout"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} ({self.user.username})"


class Order(models.Model):
    """Customer Orders tracking matching Figma's exact schema"""

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("In Production", "In Production"),
        ("Ready", "Ready"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    FABRIC_CHOICES = [
        ("shop", "Shop Fabric"),
        ("own", "Own Fabric"),
    ]

    PICKUP_STATUS_CHOICES = [
        ("Pickup Requested", "Pickup Requested"),
        ("Rider Assigned", "Rider Assigned"),
        ("Fabric Collected", "Fabric Collected"),
        ("Fabric Delivered to Tailor Shop", "Fabric Delivered to Tailor Shop"),
    ]

    TRIAL_STATUS_CHOICES = [
        ("Requested", "Requested"),
        ("Scheduled", "Scheduled"),
        ("Completed", "Completed"),
    ]

    # Base Order Info
    order_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    product_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    # Fabric & Pickup Logic
    fabric_source = models.CharField(
        max_length=10, choices=FABRIC_CHOICES, default="shop"
    )
    pickup_address = models.TextField(blank=True, null=True)
    pickup_status = models.CharField(
        max_length=50, choices=PICKUP_STATUS_CHOICES, blank=True, null=True
    )
    rider_name = models.CharField(
        max_length=100, blank=True, null=True
    )  # Will become a ForeignKey to Rider model later

    # Trial Logic
    trial_requested = models.BooleanField(default=False)
    trial_status = models.CharField(
        max_length=20, choices=TRIAL_STATUS_CHOICES, blank=True, null=True
    )
    trial_date = models.DateTimeField(blank=True, null=True)

    # Saved Measurement Snapshot
    measurement_profile = models.ForeignKey(
        MeasurementProfile, on_delete=models.SET_NULL, null=True, blank=True
    )
    profile_name_snapshot = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.order_id} - {self.product_name}"
