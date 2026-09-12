from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Design


def home(request):
    return render(request, "core/home.html")


def gallery(request):
    return render(request, "core/gallery.html")


def pricing(request):
    return render(request, "core/pricing.html")


def contact(request):
    return render(request, "core/contact.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("customers:dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("customers:dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "core/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("customers:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("customers:dashboard")
    else:
        form = UserCreationForm()

    return render(request, "core/register.html", {"form": form})


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
