from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, MeasurementProfile, CartItem
from core.models import Design


@login_required
def dashboard(request):
    # Fetch real orders from the database for the logged-in user
    user_orders = Order.objects.filter(user=request.user).order_by("-date")

    active_orders = user_orders.exclude(status__in=["Delivered", "Cancelled"])
    completed_orders = user_orders.filter(status="Delivered")

    # Calculate total spent safely from completed/all orders
    total_spent = sum(order.total_price for order in completed_orders)

    context = {
        "active_orders": active_orders,
        "recent_orders": user_orders[:5],  # Last 5 orders
        "active_count": active_orders.count(),
        "completed_count": completed_orders.count(),
        "total_spent": total_spent,
    }
    return render(request, "customers/dashboard.html", context)


@login_required
def profiles(request):
    # Fetch real measurement profiles from the database
    user_profiles = MeasurementProfile.objects.filter(user=request.user)
    return render(request, "customers/profiles.html", {"profiles": user_profiles})


@login_required
def customer_orders(request):
    # Fetch all orders belonging to the user
    orders = Order.objects.filter(user=request.user).order_by("-date")
    return render(request, "customers/orders.html", {"orders": orders})


@login_required
def customer_cart(request):
    # Fetch real cart items for the user
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.price * item.quantity for item in cart_items)
    return render(
        request, "customers/cart.html", {"cart_items": cart_items, "total": total}
    )


@login_required
def add_to_cart(request, pk):
    """Handles adding a marketplace design item into the cart"""
    design = get_object_or_404(Design, pk=pk)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product_name=design.title,
        defaults={
            "shop_name": design.shop_name,
            "price": design.price,
            "image_url": design.image_url if hasattr(design, "image_url") else "",
            "quantity": 1,
        },
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("customers:cart")


@login_required
def customer_checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if request.method == "POST":
        # Convert items in cart to formal Orders in the database
        import uuid

        for item in cart_items:
            Order.objects.create(
                order_id=f"ORD-{uuid.uuid4().hex[:6].upper()}",
                user=request.user,
                customer_name=request.user.get_full_name() or request.user.username,
                product_name=item.product_name,
                shop_name=item.shop_name,
                total_price=item.price * item.quantity,
                status="Pending",
            )
        # Clear the user's cart after a successful checkout
        cart_items.delete()
        return redirect("customers:orders")

    total = sum(item.price * item.quantity for item in cart_items)
    return render(
        request, "customers/checkout.html", {"cart_items": cart_items, "total": total}
    )


@login_required
def customer_notifications(request):
    return render(request, "customers/notifications.html")


@login_required
def customer_settings(request):
    return render(request, "customers/settings.html")


@login_required
def customer_chat(request):
    return render(request, "customers/chat.html")
