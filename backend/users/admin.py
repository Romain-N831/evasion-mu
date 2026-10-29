from django.contrib import admin

from .models import Customer, CustomerActivityLog


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Manage customer profile and verification state without exposing codes."""
    list_display = ("user", "phone_number", "contact_preference", "is_verified", "created_at")
    list_filter = ("is_verified", "contact_preference", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    readonly_fields = ("created_at", "updated_at", "verification_code_expires_at")
    exclude = ("verification_code",)


@admin.register(CustomerActivityLog)
class CustomerActivityLogAdmin(admin.ModelAdmin):
    list_display = ("customer", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("customer__user__username", "action", "details")
    readonly_fields = ("customer", "action", "details", "created_at")
