from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
import random
import string

from .models import Order, MeasurementProfile, CartItem
from core.models import Design


def generate_order_id():
    """Generates a random 8-character alphanumeric order ID"""
    return "ORD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


@login_required(login_url="/login/")
def dashboard(request):
    user_orders = Order.objects.filter(user=request.user).order_by("-date")
    active_orders = user_orders.exclude(status__in=["Delivered", "Cancelled"])
    completed_orders = user_orders.filter(status="Delivered")
    total_spent = sum(order.total_price for order in completed_orders)

    context = {
        "active_orders": active_orders,
        "recent_orders": user_orders[:5],
        "active_count": active_orders.count(),
        "completed_count": completed_orders.count(),
        "total_spent": total_spent,
    }
    return render(request, "customers/dashboard.html", context)


@login_required(login_url="/login/")
def profiles(request):
    user_profiles = MeasurementProfile.objects.filter(user=request.user)
    return render(request, "customers/profiles.html", {"profiles": user_profiles})


@login_required(login_url="/login/")
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-date")
    return render(request, "customers/orders.html", {"orders": orders})


@login_required(login_url="/login/")
def customer_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.price * item.quantity for item in cart_items)
    return render(
        request, "customers/cart.html", {"cart_items": cart_items, "total": total}
    )


@login_required(login_url="/login/")
def add_to_cart(request, pk):
    design = get_object_or_404(Design, pk=pk)

    # Use the new model relationships (design.shop.name and design.image.url)
    shop_name = design.shop.name if design.shop else "Independent Tailor"
    img_url = design.image.url if design.image else ""

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product_name=design.title,
        defaults={
            "shop_name": shop_name,
            "price": design.price,
            "image_url": img_url,
            "quantity": 1,
        },
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{design.title} added to your cart!")
    return redirect("customers:cart")


@login_required(login_url="/login/")
def customer_checkout(request):
    """Handles checking out items currently in the cart using saved profiles"""
    cart_items = CartItem.objects.filter(user=request.user)
    profiles = MeasurementProfile.objects.filter(user=request.user)

    # Auto-create a default profile if none exist so the dropdown isn't empty
    if not profiles.exists():
        MeasurementProfile.objects.create(
            user=request.user,
            name="Default Sizing Profile",
            gender="Male",
            category="Panjabi",
            is_default=True,
        )
        profiles = MeasurementProfile.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("customers:cart")

    if request.method == "POST":
        fabric_source = request.POST.get("fabric_source", "shop")
        pickup_address = request.POST.get("pickup_address", "").strip()
        trial_requested = (
            request.POST.get("trial_requested") == "on"
            or request.POST.get("trial") == "on"
        )
        profile_id = request.POST.get("measurement_profile")

        if not profile_id:
            messages.error(
                request, "Please select a measurement profile from the dropdown."
            )
            return redirect("customers:checkout")

        profile = get_object_or_404(
            MeasurementProfile, id=profile_id, user=request.user
        )
        phone = (
            request.user.profile.phone if hasattr(request.user, "profile") else "N/A"
        )

        for item in cart_items:
            order_obj = Order.objects.create(
                order_id=generate_order_id(),
                user=request.user,
                customer_name=request.user.get_full_name() or request.user.username,
                phone=phone,
                product_name=item.product_name,
                shop_name=item.shop_name,
                total_price=item.price * item.quantity,
                status="Pending",
                fabric_source=fabric_source,
                pickup_address=pickup_address if fabric_source == "own" else None,
                pickup_status="Pickup Requested" if fabric_source == "own" else None,
                trial_requested=trial_requested,
                trial_status="Requested" if trial_requested else None,
                measurement_profile=profile,
                profile_name_snapshot=profile.name,
            )

        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect("customers:order_success", order_id=order_obj.order_id)

    total = sum(item.price * item.quantity for item in cart_items)
    return render(
        request,
        "customers/checkout.html",
        {"cart_items": cart_items, "total": total, "profiles": profiles},
    )


@login_required(login_url="/login/")
def direct_checkout(request, design_id):
    """Handles bypassing the cart and checking out a single design directly"""
    design = get_object_or_404(Design, id=design_id)
    profiles = MeasurementProfile.objects.filter(user=request.user)

    if request.method == "POST":
        fabric_source = request.POST.get("fabric_source", "shop")
        pickup_address = request.POST.get("pickup_address", "").strip()
        trial_requested = request.POST.get("trial_requested") == "on"
        profile_id = request.POST.get("measurement_profile")

        if not profile_id:
            messages.error(request, "Please select a measurement profile.")
            return redirect("customers:direct_checkout", design_id=design.id)

        profile = get_object_or_404(
            MeasurementProfile, id=profile_id, user=request.user
        )
        phone = request.user.profile.phone if hasattr(request.user, "profile") else ""
        shop_name = design.shop.name if design.shop else "Independent Tailor"

        new_order = Order.objects.create(
            order_id=generate_order_id(),
            user=request.user,
            customer_name=request.user.get_full_name() or request.user.username,
            phone=phone,
            product_name=design.title,
            shop_name=shop_name,
            total_price=design.price,
            status="Pending",
            fabric_source=fabric_source,
            pickup_address=pickup_address if fabric_source == "own" else None,
            pickup_status="Pickup Requested" if fabric_source == "own" else None,
            trial_requested=trial_requested,
            trial_status="Requested" if trial_requested else None,
            measurement_profile=profile,
            profile_name_snapshot=profile.name,
        )

        messages.success(request, "Order placed successfully!")
        return redirect("customers:order_success", order_id=new_order.order_id)

    return render(
        request,
        "customers/direct_checkout.html",
        {
            "design": design,
            "profiles": profiles,
        },
    )


@login_required(login_url="/login/")
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "customers/order_success.html", {"order": order})


@login_required(login_url="/login/")
def customer_notifications(request):
    return render(request, "customers/notifications.html")


@login_required(login_url="/login/")
def customer_settings(request):
    return render(request, "customers/settings.html")


@login_required(login_url="/login/")
def customer_chat(request):
    return render(request, "customers/chat.html")


@login_required(login_url="/login/")
def manage_profiles(request):
    """Allows customers to view, add, or manage their measurement profiles"""
    user_profiles = MeasurementProfile.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "My Profile")
        relation = request.POST.get("relation", "Self")
        gender = request.POST.get("gender", "Male")
        category = request.POST.get("category", "Panjabi")
        is_default = request.POST.get("is_default") == "on"

        # Capture dynamic key-value measurements submitted from the form inputs
        # e.g., measure_chest -> {"Chest": "40"}
        values = {}
        for key, value in request.POST.items():
            if key.startswith("measure_"):
                field_name = key.replace("measure_", "").replace("_", " ").title()
                if value.strip():
                    values[field_name] = value.strip()

        # If set as default, clear other defaults for this user
        if is_default:
            MeasurementProfile.objects.filter(user=request.user).update(
                is_default=False
            )

        # Create and save using the correct 'values' JSONField from models.py
        MeasurementProfile.objects.create(
            user=request.user,
            name=name,
            relation=relation,
            gender=gender,
            category=category,
            is_default=is_default,
            values=values,  # Matches the JSONField in MeasurementProfile model
        )

        messages.success(request, "Measurement profile added successfully!")
        return redirect("customers:profiles")

    return render(request, "customers/profiles.html", {"profiles": user_profiles})


@login_required(login_url="/login/")
def checkout(request, design_id):
    """Handles the multi-step Figma-inspired custom order checkout flow"""
    design = get_object_or_404(Design, id=design_id)

    # Ensure the user has at least one default profile so the dropdown isn't empty
    profiles = MeasurementProfile.objects.filter(user=request.user)
    if not profiles.exists():
        MeasurementProfile.objects.create(
            user=request.user,
            name="Default Sizing Profile",
            gender=design.gender,
            category=design.category,
            is_default=True,
        )
        profiles = MeasurementProfile.objects.filter(user=request.user)

    if request.method == "POST":
        fabric_source = request.POST.get("fabric_source", "shop")
        pickup_address = request.POST.get("pickup_address", "").strip()
        trial_requested = (
            request.POST.get("trial_requested") == "on"
            or request.POST.get("trial") == "on"
        )
        profile_id = request.POST.get("measurement_profile")

        if not profile_id:
            messages.error(request, "Please select a measurement profile on step 3.")
            return redirect("customers:checkout", design_id=design.id)

        profile = get_object_or_404(
            MeasurementProfile, id=profile_id, user=request.user
        )
        phone = (
            request.user.profile.phone if hasattr(request.user, "profile") else "N/A"
        )
        shop_name = design.shop.name if design.shop else "Independent Tailor"

        fabric_cost = 77.00 if fabric_source == "shop" else 0.00
        pickup_fee = 3.00 if fabric_source == "own" else 0.00
        total_price = float(design.price) + fabric_cost + 5.00 + 4.00 + pickup_fee

        new_order = Order.objects.create(
            order_id=generate_order_id(),
            user=request.user,
            customer_name=request.user.get_full_name() or request.user.username,
            phone=phone,
            product_name=design.title,
            shop_name=shop_name,
            total_price=total_price,
            status="Pending",
            fabric_source=fabric_source,
            pickup_address=pickup_address if fabric_source == "own" else None,
            pickup_status="Pickup Requested" if fabric_source == "own" else None,
            trial_requested=trial_requested,
            trial_status="Requested" if trial_requested else None,
            measurement_profile=profile,
            profile_name_snapshot=profile.name,
        )

        messages.success(request, "Custom order placed successfully!")
        return redirect("customers:order_success", order_id=new_order.order_id)

    context = {
        "design": design,
        "profiles": profiles,
        "total": float(design.price) + 77.00 + 5.00 + 4.00,
    }
    return render(request, "customers/checkout.html", context)


@login_required(login_url="/login/")
def create_profile(request):
    """Alias view to handle /measurements/new/ requests securely"""
    if request.method == "POST":
        name = request.POST.get("name", "My Profile")
        relation = request.POST.get("relation", "Self")
        gender = request.POST.get("gender", "Male")
        category = request.POST.get("category", "Panjabi")
        is_default = request.POST.get("is_default") == "on"

        values = {}
        for key, value in request.POST.items():
            if key.startswith("measure_"):
                field_name = key.replace("measure_", "").replace("_", " ").title()
                if value.strip():
                    values[field_name] = value.strip()

        if is_default:
            MeasurementProfile.objects.filter(user=request.user).update(
                is_default=False
            )

        MeasurementProfile.objects.create(
            user=request.user,
            name=name,
            relation=relation,
            gender=gender,
            category=category,
            is_default=is_default,
            values=values,
        )

        messages.success(request, "Measurement profile saved successfully!")
        return redirect("customers:profiles")

    return render(request, "measurements/form.html")


@login_required
def measurement_form_view(request, pk=None):
    profile = None
    if pk:
        profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "My Profile")
        relation = request.POST.get("relation", "Self")
        gender = request.POST.get("gender", "Male")
        category = request.POST.get("category", "Panjabi")
        is_default = request.POST.get("is_default") == "on"

        # Capture all individual measure_* inputs from the form and pack them into a dictionary
        values = {}
        for key, value in request.POST.items():
            if key.startswith("measure_") and value.strip():
                field_name = key.replace("measure_", "").replace("_", " ").title()
                values[field_name] = value.strip()

        if is_default:
            # Unmark other defaults for this user
            MeasurementProfile.objects.filter(user=request.user).update(
                is_default=False
            )

        if profile:
            # Update existing profile
            profile.name = name
            profile.relation = relation
            profile.gender = gender
            profile.category = category
            profile.is_default = is_default
            profile.values = values
            profile.save()
        else:
            # Create new profile
            MeasurementProfile.objects.create(
                user=request.user,
                name=name,
                relation=relation,
                gender=gender,
                category=category,
                is_default=is_default,
                values=values,
            )

        messages.success(request, "Measurement profile saved successfully!")
        return redirect("customers:profiles")

    return render(request, "measurements/form.html", {"profile": profile})
