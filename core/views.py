from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Design
from django.contrib.auth import logout


def home(request):
    return render(request, "core/home.html")


def gallery(request):
    return render(request, "core/gallery.html")


def pricing(request):
    return render(request, "core/pricing.html")


def contact(request):
    return render(request, "core/contact.html")


def redirect_based_on_role(user):
    """Helper function to route users to their correct dashboard based on profile role."""
    try:
        role = user.profile.role
        if role == "Tailor":
            return redirect(
                "tailors:dashboard"
            )  # Adjust name based on your tailor urls
        elif role == "Rider":
            return redirect("riders:dashboard")  # Adjust name based on your rider urls
        elif user.is_superuser or role == "Admin":
            return redirect("/admin/")
    except Exception:
        pass
    return redirect("customers:dashboard")  # Default fallback for Customers


def login_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # form.get_user() is safer and cleaner in Django than manual authenticate() after validation
            user = form.get_user()
            login(request, user)
            return redirect_based_on_role(user)
    else:
        form = AuthenticationForm()

    return render(request, "core/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("customers:dashboard")

    if request.method == "POST":
        role = request.POST.get("role", "Customer")

        # Extract fields dynamically based on selected tab
        if role == "Tailor":
            username = request.POST.get("username_tailor")
            email = request.POST.get("email_tailor")
            password = request.POST.get("password_tailor")
            shop_name = request.POST.get("shop_name")

            if username and password and email:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                UserProfile.objects.create(
                    user=user, role="Tailor", shop_name=shop_name
                )
                login(request, user)
                return redirect("tailors:dashboard")  # Or tailor dashboard URL

        elif role == "Rider":
            username = request.POST.get("username_rider")
            password = request.POST.get("password_rider")
            vehicle_type = request.POST.get("vehicle_type", "Motorcycle")

            if username and password:
                user = User.objects.create_user(username=username, password=password)
                UserProfile.objects.create(
                    user=user, role="Rider", vehicle_type=vehicle_type
                )
                login(request, user)
                return redirect("riders:dashboard")  # Or rider dashboard URL

        else:  # Customer
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")

            if username and password:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                UserProfile.objects.create(user=user, role="Customer")
                login(request, user)
                return redirect("customers:dashboard")

    return render(request, "core/register.html")


def tailor_list(request):
    return render(request, "core/tailor_list.html")


def tailor_details(request):
    return render(request, "core/tailor_details.html")


def marketplace_gallery_view(request):
    designs_list = Design.objects.all().order_by("-created_at")
    return render(request, "core/marketplace.html", {"designs": designs_list})


def marketplace_detail_view(request, pk):
    # Fetches a specific design item from the database using its ID (pk)
    design = get_object_or_404(Design, pk=pk)
    return render(request, "core/marketplace_detail.html", {"design": design})


def gallery_view(request):
    # Fetch all design items to show in the public gallery
    gallery_items = Design.objects.all().order_by("-created_at")
    return render(request, "core/gallery.html", {"gallery_items": gallery_items})


def logout_view(request):
    logout(request)
    return redirect("core:home")
