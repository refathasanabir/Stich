from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages
from tailors.models import TailorShop

from .models import Design, UserProfile
from adminpanel.models import Approval
from adminpanel.models import Approval

def home(request):
    return render(request, "core/home.html")


def gallery(request):
    return render(request, "core/gallery.html")


def pricing(request):
    return render(request, "core/pricing.html")


def contact(request):
    return render(request, "core/contact.html")


# =========================================================
# ROLE REDIRECTION
# =========================================================

def redirect_based_on_role(user):
    """Route users to the correct dashboard based on their role."""

    # Admin / Staff / Superuser
    if user.is_staff or user.is_superuser:
        return redirect("adminpanel:dashboard")

    try:
        role = user.profile.role
    except UserProfile.DoesNotExist:
        role = "Customer"

    # Tailor
    if role == "Tailor":
        return redirect("tailors:dashboard")

    # Rider
    elif role == "Rider":
        return redirect("riders:dashboard")

    # Admin profile
    elif role == "Admin":
        return redirect("adminpanel:dashboard")

    # Customer
    return redirect("customers:dashboard")


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect_based_on_role(user)

    else:
        form = AuthenticationForm()

    return render(
        request,
        "core/login.html",
        {"form": form}
    )


# =========================================================
# REGISTER
# =========================================================

# Add this to your imports at the top!

# ... (keep your home, login_view, etc) ...


def register_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    if request.method == "POST":
        role = request.POST.get("role", "").strip()

        # =====================================================
        # TAILOR
        # =====================================================
        if role == "Tailor":
            username = request.POST.get("username_tailor", "").strip()
            email = request.POST.get("email_tailor", "").strip()
            phone = request.POST.get("phone_tailor", "").strip()
            password = request.POST.get("password_tailor", "")
            shop_name = request.POST.get("shop_name", "").strip()

            if not username or not password or not email or not shop_name:
                messages.error(request, "Please fill in all required Tailor fields.")
                return render(request, "core/register.html")

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
                return render(request, "core/register.html")

            # 1. Create Base User and lock it
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.is_active = False
            user.save()

            # 2. Create UserProfile (with Pending status)
            UserProfile.objects.create(
                user=user,
                role="Tailor",
                approval_status="Pending Approval",
                phone=phone,
            )

            # 3. Create linked TailorShop
            TailorShop.objects.create(owner=user, name=shop_name)

            # 4. Create the Admin Approval Record
            Approval.objects.create(user=user, role="Tailor", status="Pending")

            messages.success(
                request, "Tailor account created successfully! Awaiting Admin approval."
            )
            return redirect("core:login")

        # =====================================================
        # RIDER
        # =====================================================
        elif role == "Rider":
            username = request.POST.get("username_rider", "").strip()
            phone = request.POST.get("phone_rider", "").strip()
            password = request.POST.get("password_rider", "")
            vehicle_type = request.POST.get("vehicle_type", "Motorcycle")

            if not username or not password:
                messages.error(request, "Please fill in all required Rider fields.")
                return render(request, "core/register.html")

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
                return render(request, "core/register.html")

            # 1. Create Base User and lock it
            user = User.objects.create_user(username=username, password=password)
            user.is_active = False
            user.save()

            # 2. Create UserProfile
            UserProfile.objects.create(
                user=user,
                role="Rider",
                approval_status="Pending Approval",
                vehicle_type=vehicle_type,
                phone=phone,
            )

            # 3. Create the Admin Approval Record
            Approval.objects.create(user=user, role="Rider", status="Pending")

            messages.success(
                request, "Rider account created successfully! Awaiting Admin approval."
            )
            return redirect("core:login")

        # =====================================================
        # CUSTOMER
        # =====================================================
        elif role == "Customer":
            username = request.POST.get("username_customer", "").strip()
            email = request.POST.get("email_customer", "").strip()
            phone = request.POST.get("phone_customer", "").strip()
            password = request.POST.get("password_customer", "")

            if not username or not password:
                messages.error(request, "Please fill in all required Customer fields.")
                return render(request, "core/register.html")

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken.")
                return render(request, "core/register.html")

            user = User.objects.create_user(
                username=username, email=email, password=password
            )

            UserProfile.objects.create(
                user=user,
                role="Customer",
                approval_status="Pending Approval",
                phone=phone,
            )

            messages.success(
                request,
                "Customer account created successfully! Awaiting Admin approval.",
            )
            return redirect("core:login")

        else:
            messages.error(request, "Please select a valid account type.")

    return render(request, "core/register.html")


# =========================================================
# PUBLIC PAGES
# =========================================================

def tailor_list(request):
    return render(
        request,
        "core/tailor_list.html"
    )


def tailor_details(request):
    return render(
        request,
        "core/tailor_details.html"
    )


def marketplace_gallery_view(request):

    designs_list = Design.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "core/marketplace.html",
        {"designs": designs_list}
    )


def marketplace_detail_view(request, pk):

    design = get_object_or_404(
        Design,
        pk=pk
    )

    return render(
        request,
        "core/marketplace_detail.html",
        {"design": design}
    )


def gallery_view(request):

    gallery_items = Design.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "core/gallery.html",
        {"gallery_items": gallery_items}
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("core:home")
