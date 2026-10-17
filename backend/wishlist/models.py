from django.db import models
from django.db.models import Q


class Wishlist(models.Model):
    customer = models.OneToOneField("users.Customer", on_delete=models.CASCADE, related_name="wishlist")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist — {self.customer}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    activity = models.ForeignKey("activities.Activity", on_delete=models.CASCADE,
                                 null=True, blank=True, related_name="wishlist_items")
    room_type = models.ForeignKey("hotels.RoomType", on_delete=models.CASCADE,
                                  null=True, blank=True, related_name="wishlist_items")
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_added"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(activity__isnull=False, room_type__isnull=True) |
                           Q(activity__isnull=True, room_type__isnull=False)),
                name="wishlist_item_has_one_target"),
            models.UniqueConstraint(fields=["wishlist", "activity"], condition=Q(activity__isnull=False),
                                    name="unique_wishlist_activity"),
            models.UniqueConstraint(fields=["wishlist", "room_type"], condition=Q(room_type__isnull=False),
                                    name="unique_wishlist_room_type"),
        ]

    def __str__(self):
        return f"{self.wishlist} — {self.activity or self.room_type}"
