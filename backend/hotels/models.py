from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    star_rating = models.PositiveSmallIntegerField(null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="room_types")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    max_occupancy = models.PositiveSmallIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["hotel__name", "name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price_per_night__gte=0), name="room_price_non_negative"),
            models.CheckConstraint(condition=models.Q(total_rooms__gte=1), name="room_type_has_rooms"),
        ]

    def __str__(self):
        return f"{self.hotel.name} — {self.name}"


class RoomAvailability(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="availability_dates")
    date = models.DateField()
    available_rooms = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["room_type", "date"], name="unique_room_availability_per_date"),
            models.CheckConstraint(condition=models.Q(price_override__isnull=True) | models.Q(price_override__gte=0),
                                   name="room_price_override_non_negative"),
        ]

    def __str__(self):
        return f"{self.room_type} — {self.date}: {self.available_rooms} available"
