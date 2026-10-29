from django.contrib import admin

from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ("date_added",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("customer", "date_added")
    search_fields = ("customer__user__username",)
    readonly_fields = ("date_added",)
    inlines = [WishlistItemInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("wishlist", "activity", "room_type", "date_added")
    list_filter = ("date_added",)
    search_fields = ("wishlist__customer__user__username", "activity__title", "room_type__name")
    readonly_fields = ("date_added",)
