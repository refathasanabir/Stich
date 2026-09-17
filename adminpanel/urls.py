from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [

    # Dashboard
    path(
        "",
        views.dashboard,
        name="dashboard"
    ),

    # =====================================================
    # USERS
    # =====================================================

    path(
        "approvals/",
        views.approvals,
        name="approvals"
    ),

    path(
        "approvals/<int:approval_id>/approve/",
        views.approve_approval,
        name="approve_approval"
    ),

    path(
        "approvals/<int:approval_id>/reject/",
        views.reject_approval,
        name="reject_approval"
    ),

    path(
        "customers/",
        views.customers,
        name="customers"
    ),

    path(
        "tailor-shops/",
        views.tailor_shops,
        name="tailor_shops"
    ),

    path(
        "riders/",
        views.riders,
        name="riders"
    ),

    # =====================================================
    # ORDERS
    # =====================================================

    path(
        "orders/",
        views.orders,
        name="orders"
    ),

    # =====================================================
    # MANAGEMENT
    # =====================================================

    path(
        "management/categories/",
        views.categories,
        name="categories"
    ),

    path(
        "management/measurements/",
        views.measurements,
        name="measurements"
    ),

    path(
        "management/delivery-charges/",
        views.delivery_charges,
        name="delivery_charges"
    ),

    path(
        "management/commission-rules/",
        views.commission_rules,
        name="commission_rules"
    ),

    path(
        "management/campaigns/",
        views.campaigns,
        name="campaigns"
    ),

    # =====================================================
    # REPORTS
    # =====================================================

    path(
        "reports/",
        views.revenue_reports,
        name="revenue_reports"
    ),

    path(
        "reports/monthly/",
        views.monthly_sales_reports,
        name="monthly_sales_reports"
    ),

    path(
        "reports/statistics/",
        views.order_statistics,
        name="order_statistics"
    ),

    # =====================================================
    # REPORT EXPORTS
    # =====================================================

    path(
        "reports/export/csv/",
        views.export_revenue_csv,
        name="export_revenue_csv"
    ),

    path(
        "reports/monthly/<int:year>/<int:month>/pdf/",
        views.monthly_report_pdf,
        name="monthly_report_pdf"
    ),
    path("profile/", views.profile, name="profile"),
]