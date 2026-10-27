from django.contrib import admin
from .models import Hotel, RoomType, RoomAvailability

admin.site.register(Hotel)
admin.site.register(RoomType)
admin.site.register(RoomAvailability)

class RoomAvailabilityInline(admin.TabularInline):

    model = RoomAvailability
    extra = 1


class RoomTypeInline(admin.TabularInline):

    model = RoomType
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "city",
        "region",
        "star_rating",
        "is_active",
    )

    list_filter = (
        "region",
        "star_rating",
        "is_active",
    )

    search_fields = (
        "name",
        "city",
        "region",
    )

    fieldsets = (
        ("Hotel Information", {
            "fields": (
                "name",
                "description",
                "image_url",
            )
        }),

        ("Location", {
            "fields": (
                "address",
                "city",
                "region",
            )
        }),

        ("Other Information", {
            "fields": (
                "star_rating",
                "is_active",
            )
        }),
    )

    inlines = [RoomTypeInline]


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "hotel",
        "max_occupancy",
        "price_per_night",
        "total_rooms",
        "is_active",
    )

    list_filter = (
        "hotel",
        "is_active",
    )

    search_fields = (
        "name",
        "hotel__name",
    )

    inlines = [RoomAvailabilityInline]


@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(admin.ModelAdmin):

    list_display = (
        "room_type",
        "date",
        "available_rooms",
        "price_override",
    )

    list_filter = (
        "date",
        "room_type",
    )

    search_fields = (
        "room_type__name",
        "room_type__hotel__name",
    )
