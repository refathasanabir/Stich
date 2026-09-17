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
    cart_items = CartItem.objects.filter(user=request.user)
    profiles = MeasurementProfile.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("customers:cart")

    if request.method == "POST":
        fabric_source = request.POST.get("fabric_source", "shop")
        pickup_address = request.POST.get("pickup_address", "").strip()
        trial_requested = request.POST.get("trial_requested") == "on"
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
            Order.objects.create(
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
        return redirect("customers:orders")

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
