from django.db import models
from django.contrib.auth.models import User

# If your Design model is in core.models, import it here:
# from core.models import Design
# (If Design is in this same file, make sure it's defined above CartItem)


class GlobalMeasurementField(models.Model):
    """Admin manages master fields like Shoulder, Collar, Height, Width, etc."""

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MeasurementProfile(models.Model):
    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female")]
    RELATION_CHOICES = [("Self", "Myself"), ("Family", "Family Member")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default="Self")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    category = models.CharField(max_length=50)

    # Standard dynamic storage for values in inches
    chest = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shoulders = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    sleeve_length = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    collar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

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
    # Assuming Design model exists (adjust field or import if located in core app)
    # design = models.ForeignKey('core.Design', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} ({self.user.username})"


class Order(models.Model):
    """Customer Orders tracking"""

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Stitching", "Stitching"),
        ("Ready", "Ready"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    order_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )  # Linked user reference
    customer_name = models.CharField(max_length=100, default="Rahim Ahmed")
    product_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    measurement_profile = models.ForeignKey(
        MeasurementProfile, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.order_id} - {self.product_name}"
