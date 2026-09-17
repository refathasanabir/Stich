from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth import update_session_auth_hash
from datetime import date, datetime
from decimal import Decimal
import csv
import calendar
from tailors.models import TailorShop
from .models import (
    Approval,
    ClothingCategory,
    MeasurementCategory,
    DeliveryChargeRule,
    CommissionRule,
    Campaign,
)

from customers.models import Order, MeasurementProfile
from core.models import UserProfile


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user):
    return user.is_authenticated and user.is_staff


# =========================================================
# DASHBOARD
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def dashboard(request):

    orders = Order.objects.all()

    context = {
        "total_orders": orders.count(),

        "total_customers": MeasurementProfile.objects.values(
            "user"
        ).distinct().count(),

        "pending_orders": orders.filter(
            status="Pending"
        ).count(),

        "delivered_orders": orders.filter(
            status="Delivered"
        ).count(),

        "recent_orders": orders.order_by("-date")[:5],
    }

    return render(
        request,
        "adminpanel/dashboard.html",
        context
    )


# =========================================================
# APPROVALS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def approvals(request):
    active_tab = request.GET.get("tab", "shops")
    query = request.GET.get("q", "").strip()

    if active_tab == "riders":
        approvals = Approval.objects.filter(
            role="Rider",
            status="Pending"
        ).select_related("user")

        if query:
            approvals = approvals.filter(
                Q(user__username__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query)
            )

    else:
        active_tab = "shops"

        approvals = Approval.objects.filter(
            role="Tailor",
            status="Pending"
        ).select_related("user")

        if query:
            approvals = approvals.filter(
                Q(user__username__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__shop__name__icontains=query)
            )

    context = {
        "approvals": approvals,
        "active_tab": active_tab,
        "query": query,
    }

    return render(
        request,
        "adminpanel/approvals.html",
        context
    )


@user_passes_test(is_admin, login_url="/login/")
def approve_approval(request, approval_id):
    if request.method == "POST":
        approval = get_object_or_404(Approval, id=approval_id)

        # 1. Update Approval record
        approval.status = "Approved"
        approval.reviewed_at = timezone.now()
        approval.save()

        # 2. Activate User
        approval.user.is_active = True
        approval.user.save()

        # 3. Sync Profile Status (NEW)
        profile = approval.user.profile
        profile.approval_status = "Approved"
        profile.save()

        messages.success(request, "Account approved successfully.")
    return redirect("adminpanel:approvals")


@user_passes_test(is_admin, login_url="/login/")
def reject_approval(request, approval_id):
    if request.method == "POST":
        approval = get_object_or_404(Approval, id=approval_id)

        # 1. Update Approval record
        approval.status = "Rejected"
        approval.reviewed_at = timezone.now()
        approval.save()

        # 2. Sync Profile Status (NEW)
        profile = approval.user.profile
        profile.approval_status = "Rejected"
        profile.save()

        messages.success(request, "Account rejected.")
    return redirect("adminpanel:approvals")


# =========================================================
# USERS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def customers(request):

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "All")

    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
        profile__role="Customer"
    )

    # Search
    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    customers = customers.order_by("-date_joined")

    return render(
        request,
        "adminpanel/customers.html",
        {
            "customers": customers,
            "query": query,
            "status": status,
        }
    )





@user_passes_test(is_admin, login_url="/login/")
def tailor_shops(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "All")

    # Query the TailorShop model directly instead of UserProfile
    shops = TailorShop.objects.select_related("owner")

    if query:
        shops = shops.filter(
            Q(name__icontains=query)
            | Q(owner__username__icontains=query)
            | Q(owner__email__icontains=query)
        )

    shops = shops.order_by("-created_at")

    return render(
        request,
        "adminpanel/tailor_shops.html",
        {
            "shops": shops,
            "query": query,
            "status": status,
        },
    )


@user_passes_test(is_admin, login_url="/login/")
def riders(request):

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "All")

    riders = UserProfile.objects.filter(
        role="Rider"
    ).select_related(
        "user"
    )

    if query:
        riders = riders.filter(
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query) |
            Q(vehicle_type__icontains=query)
        )

    riders = riders.order_by("-user__date_joined")

    return render(
        request,
        "adminpanel/riders.html",
        {
            "riders": riders,
            "query": query,
            "status": status,
        }
    )


# =========================================================
# ORDERS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def orders(request):
    query = request.GET.get("q", "").strip()

    orders = Order.objects.all().order_by("-date")

    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(product_name__icontains=query) |
            Q(shop_name__icontains=query)
        )

    return render(
        request,
        "adminpanel/orders.html",
        {
            "orders": orders,
            "query": query,
        }
    )


# =========================================================
# CLOTHING CATEGORIES
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def categories(request):

    if request.method == "POST":

        action = request.POST.get("action")

        # ADD
        if action == "add":

            name = request.POST.get(
                "name",
                ""
            ).strip()

            description = request.POST.get(
                "description",
                ""
            ).strip()

            if name:

                ClothingCategory.objects.create(
                    name=name,
                    description=description
                )

                messages.success(
                    request,
                    "Clothing category added."
                )

            return redirect(
                "adminpanel:categories"
            )

        # DELETE
        if action == "delete":

            category_id = request.POST.get(
                "category_id"
            )

            category = get_object_or_404(
                ClothingCategory,
                id=category_id
            )

            category.delete()

            messages.success(
                request,
                "Category deleted."
            )

            return redirect(
                "adminpanel:categories"
            )

    categories_list = ClothingCategory.objects.all()

    return render(
        request,
        "adminpanel/management/categories.html",
        {
            "categories": categories_list
        }
    )


# =========================================================
# MEASUREMENT CATEGORIES
# =========================================================

MEASUREMENT_FIELDS = [
    "Neck",
    "Shoulder",
    "Chest",
    "Waist",
    "Hip",
    "Belly",
    "Bicep",
    "Sleeve",
    "Length",
    "Back Length",
    "Inseam",
    "Bust",
    "Under-Bust",
    "Armhole",
    "Seat",
    "Thigh",
]


@user_passes_test(is_admin, login_url="/login/")
def measurements(request):

    if request.method == "POST":

        action = request.POST.get("action")

        # ADD
        if action == "add":

            name = request.POST.get(
                "name",
                ""
            ).strip()

            gender = request.POST.get(
                "gender",
                "Unisex"
            )

            fields = request.POST.getlist(
                "fields"
            )

            if name:

                MeasurementCategory.objects.create(
                    name=name,
                    gender=gender,
                    fields=fields
                )

                messages.success(
                    request,
                    "Measurement category added."
                )

            return redirect(
                "adminpanel:measurements"
            )

        # EDIT
        elif action == "edit":

            category_id = request.POST.get(
                "category_id"
            )

            category = get_object_or_404(
                MeasurementCategory,
                id=category_id
            )

            category.name = request.POST.get(
                "name",
                category.name
            ).strip()

            category.gender = request.POST.get(
                "gender",
                category.gender
            )

            category.fields = request.POST.getlist(
                "fields"
            )

            category.save()

            messages.success(
                request,
                "Measurement category updated."
            )

            return redirect(
                "adminpanel:measurements"
            )

        # DELETE
        elif action == "delete":

            category_id = request.POST.get(
                "category_id"
            )

            category = get_object_or_404(
                MeasurementCategory,
                id=category_id
            )

            category.delete()

            messages.success(
                request,
                "Measurement category deleted."
            )

            return redirect(
                "adminpanel:measurements"
            )

    categories_list = MeasurementCategory.objects.all()

    return render(
        request,
        "adminpanel/management/measurements.html",
        {
            "measurements": categories_list,
            "measurement_fields": MEASUREMENT_FIELDS,
        }
    )


# =========================================================
# DELIVERY CHARGES
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def delivery_charges(request):

    rule = DeliveryChargeRule.objects.first()

    if not rule:

        rule = DeliveryChargeRule.objects.create(
            name="Default Delivery Rule"
        )

    if request.method == "POST":

        rule.charge = request.POST.get(
            "base_charge",
            rule.charge
        )

        rule.extra_km_charge = request.POST.get(
            "extra_km_charge",
            rule.extra_km_charge
        )

        rule.min_order_amount = request.POST.get(
            "free_delivery_threshold",
            rule.min_order_amount
        )

        rule.fabric_pickup_charge = request.POST.get(
            "fabric_pickup_charge",
            rule.fabric_pickup_charge
        )

        rule.save()

        messages.success(
            request,
            "Delivery charge settings saved."
        )

        return redirect(
            "adminpanel:delivery_charges"
        )

    return render(
        request,
        "adminpanel/management/delivery_charges.html",
        {
            "rule": rule
        }
    )


# =========================================================
# COMMISSION RULES
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def commission_rules(request):

    rule = CommissionRule.objects.first()

    if not rule:

        rule = CommissionRule.objects.create(
            name="Platform Commission"
        )

    if request.method == "POST":

        rule.percentage = request.POST.get(
            "standard_rate",
            rule.percentage
        )

        rule.premium_rate = request.POST.get(
            "premium_rate",
            rule.premium_rate
        )

        rule.minimum_commission = request.POST.get(
            "minimum_commission",
            rule.minimum_commission
        )

        rule.rider_payout_share = request.POST.get(
            "rider_payout_share",
            rule.rider_payout_share
        )

        rule.save()

        messages.success(
            request,
            "Commission settings saved."
        )

        return redirect(
            "adminpanel:commission_rules"
        )

    return render(
        request,
        "adminpanel/management/commission_rules.html",
        {
            "rule": rule
        }
    )


# =========================================================
# CAMPAIGNS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def campaigns(request):

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        discount = request.POST.get(
            "discount",
            0
        )

        promo_code = request.POST.get(
            "promo_code",
            ""
        ).strip()

        audience = request.POST.getlist(
            "audience"
        )

        banner = request.FILES.get(
            "banner"
        )

        Campaign.objects.create(
            name=title,
            description=description,
            discount_percentage=discount,
            promo_code=promo_code,
            audience=audience,
            banner=banner
        )

        messages.success(
            request,
            "Campaign broadcast successfully."
        )

        return redirect(
            "adminpanel:campaigns"
        )

    campaigns_list = Campaign.objects.all()

    return render(
        request,
        "adminpanel/management/campaigns.html",
        {
            "campaigns": campaigns_list
        }
    )


# =========================================================
# REPORTS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def revenue_reports(request):

    today = timezone.localdate()

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    report_type = request.GET.get(
        "report_type",
        "Sales"
    )

    # -----------------------------------------
    # START DATE
    # -----------------------------------------

    if start_date:

        try:
            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            start = date(
                today.year,
                today.month,
                1
            )

    else:

        start = date(
            today.year,
            today.month,
            1
        )

    # -----------------------------------------
    # END DATE
    # -----------------------------------------

    if end_date:

        try:
            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            end = today

    else:

        end = today

    # -----------------------------------------
    # ORDERS
    # -----------------------------------------

    orders = Order.objects.filter(
        date__gte=start,
        date__lte=end
    ).exclude(
        status="Cancelled"
    )

    # -----------------------------------------
    # GMV
    # -----------------------------------------

    gross_merchandise_value = (
        orders.aggregate(
            total=Sum("total_price")
        )["total"]
        or Decimal("0")
    )

    # -----------------------------------------
    # TOTAL ORDERS
    # -----------------------------------------

    total_orders = orders.count()

    # -----------------------------------------
    # COMMISSION
    # -----------------------------------------

    commission_rule = CommissionRule.objects.filter(
        is_active=True
    ).first()

    if commission_rule:

        commission_rate = commission_rule.percentage

    else:

        commission_rate = Decimal("10")

    net_platform_revenue = (
        gross_merchandise_value
        * commission_rate
        / Decimal("100")
    )

    # -----------------------------------------
    # ACTIVE SHOPS
    # -----------------------------------------

    active_shops = UserProfile.objects.filter(
        role="Tailor"
    ).count()

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {
        "start_date": start,
        "end_date": end,
        "report_type": report_type,

        "gross_merchandise_value":
            gross_merchandise_value,

        "net_platform_revenue":
            net_platform_revenue,

        "total_orders":
            total_orders,

        "active_shops":
            active_shops,

        "commission_rate":
            commission_rate,
    }

    return render(
        request,
        "adminpanel/reports/revenue.html",
        context
    )


# =========================================================
# EXPORT REVENUE CSV
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def export_revenue_csv(request):

    today = timezone.localdate()

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    # -----------------------------------------
    # START DATE
    # -----------------------------------------

    if start_date:

        try:
            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            start = date(
                today.year,
                today.month,
                1
            )

    else:

        start = date(
            today.year,
            today.month,
            1
        )

    # -----------------------------------------
    # END DATE
    # -----------------------------------------

    if end_date:

        try:
            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            end = today

    else:

        end = today

    # -----------------------------------------
    # ORDERS
    # -----------------------------------------

    orders = Order.objects.filter(
        date__gte=start,
        date__lte=end
    ).exclude(
        status="Cancelled"
    ).order_by("date")

    # -----------------------------------------
    # RESPONSE
    # -----------------------------------------

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        f'attachment; '
        f'filename="stitchsync_revenue_'
        f'{start}_{end}.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Order ID",
        "Customer",
        "Product",
        "Tailor Shop",
        "Status",
        "Total Price",
        "Date",
    ])

    for order in orders:

        writer.writerow([
            order.order_id,
            order.customer_name,
            order.product_name,
            order.shop_name,
            order.status,
            order.total_price,
            order.date,
        ])

    return response


# =========================================================
# MONTHLY SALES REPORTS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def monthly_sales_reports(request):

    today = timezone.localdate()

    months = []

    # -----------------------------------------
    # COMMISSION RULE
    # -----------------------------------------

    commission_rule = CommissionRule.objects.filter(
        is_active=True
    ).first()

    if commission_rule:

        commission_rate = commission_rule.percentage

    else:

        commission_rate = Decimal("10")

    # -----------------------------------------
    # LAST 12 MONTHS
    # -----------------------------------------

    for i in range(12):

        year = today.year

        month = today.month - i

        while month <= 0:

            month += 12
            year -= 1

        start = date(
            year,
            month,
            1
        )

        last_day = calendar.monthrange(
            year,
            month
        )[1]

        end = date(
            year,
            month,
            last_day
        )

        orders = Order.objects.filter(
            date__gte=start,
            date__lte=end
        ).exclude(
            status="Cancelled"
        )

        gmv = (
            orders.aggregate(
                total=Sum("total_price")
            )["total"]
            or Decimal("0")
        )

        revenue = (
            gmv
            * commission_rate
            / Decimal("100")
        )

        months.append({
            "year": year,
            "month": month,
            "name": start.strftime(
                "%B %Y"
            ),
            "gmv": gmv,
            "orders": orders.count(),
            "revenue": revenue,
        })

    return render(
        request,
        "adminpanel/reports/monthly_sales.html",
        {
            "months": months
        }
    )


# =========================================================
# MONTHLY SALES PDF
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def monthly_report_pdf(
    request,
    year,
    month
):

    from reportlab.lib.pagesizes import A4

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    from reportlab.lib import colors

    from reportlab.lib.styles import (
        getSampleStyleSheet
    )

    from reportlab.lib.units import inch

    # -----------------------------------------
    # DATE RANGE
    # -----------------------------------------

    start = date(
        year,
        month,
        1
    )

    last_day = calendar.monthrange(
        year,
        month
    )[1]

    end = date(
        year,
        month,
        last_day
    )

    # -----------------------------------------
    # ORDERS
    # -----------------------------------------

    orders = Order.objects.filter(
        date__gte=start,
        date__lte=end
    ).exclude(
        status="Cancelled"
    )

    # -----------------------------------------
    # GMV
    # -----------------------------------------

    gmv = (
        orders.aggregate(
            total=Sum("total_price")
        )["total"]
        or Decimal("0")
    )

    # -----------------------------------------
    # COMMISSION
    # -----------------------------------------

    commission_rule = CommissionRule.objects.filter(
        is_active=True
    ).first()

    if commission_rule:

        rate = commission_rule.percentage

    else:

        rate = Decimal("10")

    revenue = (
        gmv
        * rate
        / Decimal("100")
    )

    # -----------------------------------------
    # PDF RESPONSE
    # -----------------------------------------

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; '
        f'filename="stitchsync_'
        f'{year}_{month:02d}.pdf"'
    )

    # -----------------------------------------
    # DOCUMENT
    # -----------------------------------------

    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    story = []

    # -----------------------------------------
    # TITLE
    # -----------------------------------------

    story.append(
        Paragraph(
            "StitchSync",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Monthly Sales Report — "
            f"{start.strftime('%B %Y')}",
            styles["Heading2"]
        )
    )

    story.append(
        Spacer(
            1,
            20
        )
    )

    # -----------------------------------------
    # DATA
    # -----------------------------------------

    data = [
        [
            "Metric",
            "Value"
        ],

        [
            "Gross Merchandise Value",
            f"${gmv:,.2f}"
        ],

        [
            "Net Platform Revenue",
            f"${revenue:,.2f}"
        ],

        [
            "Total Orders",
            str(orders.count())
        ],

        [
            "Commission Rate",
            f"{rate}%"
        ],
    ]

    # -----------------------------------------
    # TABLE
    # -----------------------------------------

    table = Table(
        data,
        colWidths=[
            3.8 * inch,
            2 * inch
        ]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#0A192F")
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                10
            ),
        ])
    )

    story.append(table)

    story.append(
        Spacer(
            1,
            30
        )
    )

    story.append(
        Paragraph(
            "Generated by StitchSync Admin Panel",
            styles["Normal"]
        )
    )

    # -----------------------------------------
    # BUILD PDF
    # -----------------------------------------

    document.build(story)

    return response


# =========================================================
# ORDER STATISTICS
# =========================================================

@user_passes_test(is_admin, login_url="/login/")
def order_statistics(request):

    orders = Order.objects.all()

    # -----------------------------------------
    # TOTAL ORDERS
    # -----------------------------------------

    total_orders = orders.count()

    # -----------------------------------------
    # STATUS COUNTS
    # -----------------------------------------

    delivered = orders.filter(
        status="Delivered"
    ).count()

    in_production = orders.filter(
        status="Stitching"
    ).count()

    pending = orders.filter(
        status="Pending"
    ).count()

    accepted = orders.filter(
        status="Accepted"
    ).count()

    ready = orders.filter(
        status="Ready"
    ).count()

    cancelled = orders.filter(
        status="Cancelled"
    ).count()

    # -----------------------------------------
    # ORDER VALUE
    # -----------------------------------------

    order_value = (
        orders.exclude(
            status="Cancelled"
        )
        .aggregate(
            total=Sum("total_price")
        )["total"]
        or Decimal("0")
    )

    # -----------------------------------------
    # CHART DATA
    # -----------------------------------------

    status_data = [
        {
            "name": "Pending",
            "value": pending,
        },

        {
            "name": "Accepted",
            "value": accepted,
        },

        {
            "name": "In Production",
            "value": in_production,
        },

        {
            "name": "Ready",
            "value": ready,
        },

        {
            "name": "Delivered",
            "value": delivered,
        },

        {
            "name": "Cancelled",
            "value": cancelled,
        },
    ]

    max_value = max(
        [
            item["value"]
            for item in status_data
        ] + [1]
    )

    # -----------------------------------------
    # CONTEXT
    # -----------------------------------------

    context = {
        "total_orders": total_orders,

        "delivered": delivered,

        "in_production": in_production,

        "order_value": order_value,

        "status_data": status_data,

        "max_value": max_value,
    }

    return render(
        request,
        "adminpanel/reports/order_statistics.html",
        context
    )
@user_passes_test(is_admin, login_url="/login/")
def profile(request):

    user = request.user

    if request.method == "POST":

        action = request.POST.get("action")

        # =========================================
        # SAVE ACCOUNT DETAILS
        # =========================================

        if action == "profile":

            full_name = request.POST.get(
                "full_name",
                ""
            ).strip()

            email = request.POST.get(
                "email",
                ""
            ).strip()

            user.first_name = full_name
            user.email = email

            user.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect(
                "adminpanel:profile"
            )


        # =========================================
        # CHANGE PASSWORD
        # =========================================

        elif action == "password":

            current_password = request.POST.get(
                "current_password",
                ""
            )

            new_password = request.POST.get(
                "new_password",
                ""
            )

            confirm_password = request.POST.get(
                "confirm_password",
                ""
            )


            if not user.check_password(
                current_password
            ):

                messages.error(
                    request,
                    "Current password is incorrect."
                )

                return redirect(
                    "adminpanel:profile"
                )


            if not new_password:

                messages.error(
                    request,
                    "Please enter a new password."
                )

                return redirect(
                    "adminpanel:profile"
                )


            if new_password != confirm_password:

                messages.error(
                    request,
                    "New passwords do not match."
                )

                return redirect(
                    "adminpanel:profile"
                )


            if len(new_password) < 8:

                messages.error(
                    request,
                    "Password must be at least 8 characters."
                )

                return redirect(
                    "adminpanel:profile"
                )


            user.set_password(new_password)

            user.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password updated successfully."
            )

            return redirect(
                "adminpanel:profile"
            )


    return render(
        request,
        "adminpanel/profile.html",
        {
            "user": user,
        }
    )
