import uuid
from django.core.validators import MinValueValidator
from django.db import models


class PromoCode(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Percentage"
        FIXED = "FIXED", "Fixed amount"

    code = models.CharField(max_length=40, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    uses_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(discount_value__gt=0), name="promo_discount_positive"),
            models.CheckConstraint(condition=models.Q(valid_until__gt=models.F("valid_from")),
                                   name="promo_valid_dates_ordered"),
        ]

    def __str__(self):
        return self.code


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    customer = models.ForeignKey("users.Customer", on_delete=models.PROTECT, related_name="bookings")
    booking_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       validators=[MinValueValidator(0)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="bookings")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          validators=[MinValueValidator(0)])
    ticket_reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cancellation_requested_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    reschedule_requested_for = models.DateTimeField(null=True, blank=True)
    reschedule_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-booking_date"]
        constraints = [
            models.CheckConstraint(condition=models.Q(total_amount__gte=0), name="booking_total_non_negative"),
            models.CheckConstraint(condition=models.Q(discount_amount__gte=0), name="booking_discount_non_negative"),
        ]

    def __str__(self):
        return f"Booking {self.pk} — {self.customer}"


class Reservation(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="activity_reservations")
    activity_slot = models.ForeignKey("activities.ActivitySlot", on_delete=models.PROTECT,
                                      related_name="reservations")
    participant_count = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    @property
    def scheduled_date(self):
        return self.activity_slot.starts_at

    @property
    def activity(self):
        return self.activity_slot.activity

    def __str__(self):
        return f"{self.activity} — booking {self.booking_id}"


class HotelReservation(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="hotel_reservations")
    room_type = models.ForeignKey("hotels.RoomType", on_delete=models.PROTECT, related_name="reservations")
    check_in = models.DateField()
    check_out = models.DateField()
    rooms_count = models.PositiveSmallIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2,
                                          validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(check_out__gt=models.F("check_in")),
                                   name="hotel_reservation_checkout_after_checkin"),
            models.CheckConstraint(condition=models.Q(rooms_count__gte=1), name="hotel_reservation_rooms_positive"),
            models.CheckConstraint(condition=models.Q(price_per_night__gte=0),
                                   name="hotel_reservation_price_non_negative"),
        ]

    def __str__(self):
        return f"{self.room_type} — {self.check_in} to {self.check_out}"


# Create your models here.
