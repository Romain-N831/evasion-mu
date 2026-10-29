from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Staff can approve, hide, or review pending customer feedback."""
    list_display = ("activity", "customer", "rating", "moderation_status", "created_at")
    list_filter = ("moderation_status", "rating", "created_at")
    search_fields = ("activity__title", "customer__user__username", "comment")
    readonly_fields = ("created_at", "updated_at")
