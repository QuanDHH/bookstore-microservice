from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Staff


@admin.register(Staff)
class StaffAdmin(UserAdmin):
    model = Staff
    ordering = ("id",)
    list_display = ("id", "username", "email", "full_name", "is_staff", "is_active")
    search_fields = ("username", "email", "full_name")
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal info", {"fields": ("full_name",)}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "full_name", "password1", "password2"),
            },
        ),
    )
