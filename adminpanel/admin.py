from django.contrib import admin
from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
        "status",
        "submitted_at",
        "reviewed_at",
    )

    list_filter = (
        "role",
        "status",
    )

    search_fields = (
        "user__username",
        "user__email",
    )