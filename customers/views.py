from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
import random
import string
import io
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order, MeasurementProfile, CartItem
from core.models import Design
from tailors.models import TailorShop
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from tailors.models import TailorShop
from core.models import Design
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import UserProfile
from django.db.models import Q
from tailors.models import TailorShop
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
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
    orders = Order.objects.filter(user=request.user).order_by("-date", "-id")

    sort_by = request.GET.get("sort", "newest")
    if sort_by == "oldest":
        orders = Order.objects.filter(user=request.user).order_by("date", "id")
    elif sort_by == "status":
        orders = orders.order_by("status")

    context = {
        "orders": orders,
        "selected_sort": sort_by,
    }
    return render(request, "customers/orders.html", context)


# @login_required(login_url="/login/")
# def customer_cart(request):
#     cart_items = CartItem.objects.filter(user=request.user)
#     subtotal = sum(item.price * item.quantity for item in cart_items)
#     delivery_fee = 9.00
#     total = float(subtotal) + delivery_fee

#     return render(
#         request,
#         "customers/cart.html",
#         {
#             "cart_items": cart_items,
#             "subtotal": subtotal,
#             "delivery_fee": delivery_fee,
#             "total": total,
#         },
#     )


@login_required(login_url="/login/")
def customer_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate the raw sum of all items in the cart without any modifications
    total = sum(float(item.price) * int(item.quantity) for item in cart_items)

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
        # generated_pin = str(random.randint(1000, 9999))
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
            delivery_pin=generate_pin(),
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


@login_required(login_url="/login/")
def remove_from_cart(request, pk):
    """Allows removing a specific item from the cart"""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("customers:cart")


@login_required(login_url="/login/")
def customer_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.price * item.quantity for item in cart_items)

    if request.method == "POST":
        # Redirecting from cart to the final payment page
        return redirect("customers:payment")

    return render(
        request, "customers/cart.html", {"cart_items": cart_items, "total": total}
    )


# @login_required(login_url="/login/")
# def customer_payment(request):
#     """Handles the final payment method selection and places the official order"""
#     cart_items = CartItem.objects.filter(user=request.user)

#     if not cart_items.exists():
#         messages.error(request, "Your cart is empty.")
#         return redirect("customers:cart")

#     subtotal = sum(item.price * item.quantity for item in cart_items)
#     delivery_fee = 9.00
#     total = float(subtotal) + delivery_fee

#     if request.method == "POST":
#         phone = (
#             request.user.profile.phone if hasattr(request.user, "profile") else "N/A"
#         )

#         order_obj = None
#         for item in cart_items:
#             pin = f"{random.randint(0, 9999):04d}"

#             # Save the final order total including its portion of delivery/fees if needed
#             # Or use item.price directly if it already incorporates everything.
#             order_obj = Order.objects.create(
#                 order_id=generate_order_id(),
#                 user=request.user,
#                 customer_name=request.user.get_full_name() or request.user.username,
#                 phone=phone,
#                 product_name=item.product_name,
#                 shop_name=item.shop_name,
#                 total_price=float(item.price * item.quantity),
#                 status="Pending",
#                 fabric_source=item.fabric_source,
#                 pickup_address=item.pickup_address,
#                 pickup_status=(
#                     "Pickup Requested" if item.fabric_source == "own" else None
#                 ),
#                 trial_requested=item.trial_requested,
#                 trial_status="Requested" if item.trial_requested else None,
#                 measurement_profile=item.measurement_profile,
#                 profile_name_snapshot=(
#                     item.measurement_profile.name
#                     if item.measurement_profile
#                     else "Default"
#                 ),
#                 delivery_pin=pin,
#             )

#         cart_items.delete()
#         messages.success(request, "Order placed successfully!")
#         return redirect("customers:order_success", order_id=order_obj.order_id)

#     return render(
#         request,
#         "customers/payment.html",
#         {
#             "cart_items": cart_items,
#             "subtotal": subtotal,
#             "delivery_fee": delivery_fee,
#             "total": total,
#         },
#     )


@login_required(login_url="/login/")
def customer_payment(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("customers:cart")

    total = sum(item.price * item.quantity for item in cart_items)

    if request.method == "POST":
        phone = (
            request.user.profile.phone if hasattr(request.user, "profile") else "N/A"
        )

        order_obj = None
        for item in cart_items:
            pin = f"{random.randint(0, 9999):04d}"
            order_obj = Order.objects.create(
                order_id=generate_order_id(),
                user=request.user,
                customer_name=request.user.get_full_name() or request.user.username,
                phone=phone,
                product_name=item.product_name,
                shop_name=item.shop_name,
                total_price=float(item.price * item.quantity),
                status="Pending",
                fabric_source=item.fabric_source,
                pickup_address=item.pickup_address,
                pickup_status=(
                    "Pickup Requested" if item.fabric_source == "own" else None
                ),
                trial_requested=item.trial_requested,
                trial_status="Requested" if item.trial_requested else None,
                measurement_profile=item.measurement_profile,
                profile_name_snapshot=(
                    item.measurement_profile.name
                    if item.measurement_profile
                    else "Default"
                ),
                delivery_pin=pin,
            )

        cart_items.delete()
        messages.success(request, "Order placed successfully!")
        return redirect("customers:order_success", order_id=order_obj.order_id)

    return render(
        request, "customers/payment.html", {"cart_items": cart_items, "total": total}
    )


@login_required(login_url="/login/")
def download_receipt(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header Background Accent
    p.setFillColor(colors.HexColor("#0B132B"))  # Navy
    p.rect(0, height - 100, width, 100, stroke=0, fill=1)

    # Title & Branding
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 22)
    p.drawString(40, height - 55, "StitchSync")
    p.setFont("Helvetica", 11)
    p.drawString(40, height - 75, "Official Tailored Garment Order Receipt")

    # Order Meta
    p.setFillColor(colors.HexColor("#333333"))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, height - 140, f"Order Reference: {order.order_id}")
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 160, f"Date: {order.date}")
    p.drawString(40, height - 175, f"Customer Name: {order.customer_name}")
    p.drawString(40, height - 190, f"Phone: {order.phone or 'N/A'}")

    # Divider Line
    p.setStrokeColor(colors.HexColor("#E2E8F0"))
    p.setLineWidth(1)
    p.line(40, height - 210, width - 40, height - 210)

    # Table Headers
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#0B132B"))
    p.drawString(40, height - 235, "ITEM DESCRIPTION")
    p.drawString(320, height - 235, "SHOP")
    p.drawString(460, height - 235, "AMOUNT")

    # Table Item Row
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#4A5568"))
    p.drawString(40, height - 260, order.product_name)
    p.drawString(320, height - 260, order.shop_name)
    p.drawString(460, height - 260, f"${order.total_price}")

    p.line(40, height - 280, width - 40, height - 280)

    # Specifications Summary
    p.setFont("Helvetica-Bold", 11)
    p.setFillColor(colors.HexColor("#0B132B"))
    p.drawString(40, height - 320, "Customization Summary:")

    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#4A5568"))
    p.drawString(
        40, height - 340, f"• Fabric Source: {order.fabric_source.title()} Fabric"
    )
    p.drawString(
        40,
        height - 360,
        f"• Measurement Profile: {order.profile_name_snapshot or 'Default Sizing Profile'}",
    )
    p.drawString(
        40,
        height - 380,
        f"• Fitting Trial Requested: {'Yes' if order.trial_requested else 'No'}",
    )
    p.drawString(40, height - 400, f"• Order Status: {order.status}")

    # Total Price Box
    p.setFillColor(colors.HexColor("#F8FAFC"))
    p.rect(360, height - 480, 210, 50, stroke=1, fill=1)
    p.setFillColor(colors.HexColor("#0B132B"))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(380, height - 450, "Total Paid:")
    p.setFont("Helvetica-Bold", 16)
    p.drawString(460, height - 453, f"${order.total_price}")

    # Footer note
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.HexColor("#A0AEC0"))
    p.drawCentredString(
        width / 2.0,
        50,
        "Thank you for choosing StitchSync. For support, contact your tailor directly via chat.",
    )

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(
        buffer, as_attachment=True, filename=f"Receipt_{order.order_id}.pdf"
    )


@login_required(login_url="/login/")
def order_tracking_view(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "customers/order_tracking.html", {"order": order})

import random
import string


def generate_pin():
    return "".join(random.choices(string.digits, k=4))


@login_required(login_url="/login/")
def shops_view(request):
    shops = TailorShop.objects.all()
    return render(request, "customers/shops.html", {"shops": shops})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from tailors.models import TailorShop
from core.models import Design


@login_required(login_url="/login/")
def shop_detail_view(request, shop_id):
    # Get the specific shop or return a 404 if it doesn't exist
    shop = get_object_or_404(TailorShop, id=shop_id)

    # Filter designs that belong to this specific shop
    designs = Design.objects.filter(shop=shop)

    context = {
        "shop": shop,
        "designs": designs,
    }
    return render(request, "customers/shop_detail.html", context)


@login_required(login_url="/login/")
def settings_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        # Update standard User fields
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.save()

        # Update UserProfile fields (like phone)
        profile.phone = request.POST.get("phone", profile.phone)
        profile.save()

        messages.success(
            request, "Your account settings have been updated successfully."
        )
        return redirect("customers:settings")

    return render(request, "customers/settings.html", {"profile": profile})


@login_required(login_url="/login/")
def shops_view(request):
    shops = TailorShop.objects.all()

    # Search filter by shop name or location
    search_query = request.GET.get("q", "").strip()
    if search_query:
        shops = shops.filter(
            Q(name__icontains=search_query) | Q(location__icontains=search_query)
        )

    context = {
        "shops": shops,
        "search_query": search_query,
    }
    return render(request, "customers/shops.html", context)


@login_required(login_url="/login/")
def checkout(request, design_id):
    design = get_object_or_404(Design, id=design_id)
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
            messages.error(request, "Please select a measurement profile.")
            return redirect("customers:checkout", design_id=design.id)

        profile = get_object_or_404(
            MeasurementProfile, id=profile_id, user=request.user
        )
        shop_name = design.shop.name if design.shop else "Independent Tailor"
        img_url = design.image.url if design.image else ""

        # Exact consistent fee breakdown
        base_price = float(design.price)
        fabric_fee = 77.00 if fabric_source == "shop" else 0.00
        pickup_fee = 3.00 if fabric_source == "own" else 0.00
        trial_fee = 5.00 if trial_requested else 0.00
        delivery_fee = 4.00

        item_total = base_price + fabric_fee + pickup_fee + trial_fee + delivery_fee

        CartItem.objects.create(
            user=request.user,
            product_name=design.title,
            shop_name=shop_name,
            price=item_total,
            quantity=1,
            image_url=img_url,
            fabric_source=fabric_source,
            pickup_address=pickup_address if fabric_source == "own" else None,
            trial_requested=trial_requested,
            measurement_profile=profile,
        )

        messages.success(request, f"{design.title} added to your cart!")
        return redirect("customers:cart")

    # Consistent default total matching the shop fabric + delivery + tax baseline
    default_total = float(design.price) + 77.00 + 4.00
    context = {
        "design": design,
        "profiles": profiles,
        "total": default_total,
    }
    return render(request, "customers/checkout.html", context)
