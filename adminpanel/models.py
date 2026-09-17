from django.db import models
from django.contrib.auth.models import User


class Approval(models.Model):

    ROLE_CHOICES = [
        ("Tailor", "Tailor"),
        ("Rider", "Rider"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="approvals"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role} - {self.status}"


class ClothingCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MeasurementCategory(models.Model):

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Unisex", "Unisex"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default="Unisex"
    )

    fields = models.JSONField(
        default=list,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DeliveryChargeRule(models.Model):

    name = models.CharField(
        max_length=100,
        default="Default Delivery Rule"
    )

    charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=5
    )

    extra_km_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.50
    )

    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=150
    )

    fabric_pickup_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=3
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class CommissionRule(models.Model):

    name = models.CharField(
        max_length=100,
        default="Platform Commission"
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10
    )

    premium_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=7
    )

    minimum_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=2
    )

    rider_payout_share = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Campaign(models.Model):

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    banner = models.ImageField(
        upload_to="campaigns/",
        blank=True,
        null=True
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    promo_code = models.CharField(
        max_length=50,
        blank=True
    )

    audience = models.JSONField(
        default=list,
        blank=True
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name