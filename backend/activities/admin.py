from django.contrib import admin

from .models import Activity, ActivityBlockedDate, ActivitySlot


class ActivitySlotInline(admin.TabularInline):
    """Let staff maintain an activity's scheduled slots on the activity page."""
    model = ActivitySlot
    extra = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "category", "current_price", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("title", "location", "category")
    inlines = [ActivitySlotInline]


@admin.register(ActivitySlot)
class ActivitySlotAdmin(admin.ModelAdmin):
    list_display = ("activity", "starts_at", "capacity", "is_active")
    list_filter = ("is_active", "activity")
    search_fields = ("activity__title",)
    date_hierarchy = "starts_at"


@admin.register(ActivityBlockedDate)
class ActivityBlockedDateAdmin(admin.ModelAdmin):
    list_display = ("activity", "date", "reason")
    list_filter = ("date", "activity")
    search_fields = ("activity__title", "reason")
