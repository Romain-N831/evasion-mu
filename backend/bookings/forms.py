
from django import forms
from django.db.models import Sum, Q, F
from django.utils import timezone

from activities.models import ActivitySlot, ActivityBlockedDate
from hotels.models import RoomType
from .models import Booking, PromoCode


class HotelBookingForm(forms.Form):
    """Server-side validation for one room type at a selected hotel."""

    check_in = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    check_out = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    rooms_count = forms.IntegerField(min_value=1, label="Number of rooms")
    guests_count = forms.IntegerField(min_value=1, label="Number of guests")

    def __init__(self, *args, room_type, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_type = room_type

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        rooms_count = cleaned_data.get("rooms_count")
        guests_count = cleaned_data.get("guests_count")

        if check_in and check_in < timezone.localdate():
            self.add_error("check_in", "Check-in cannot be in the past.")
        if check_in and check_out and check_out <= check_in:
            self.add_error("check_out", "Check-out must be after check-in.")
        if rooms_count and guests_count and guests_count > rooms_count * self.room_type.max_occupancy:
            self.add_error(
                "guests_count",
                f"This room type accommodates at most {self.room_type.max_occupancy} guests per room.",
            )
        return cleaned_data


# Form used by customers when booking an activity.
class ActivityBookingForm(forms.Form):

    # Customers select a date and time from existing ActivitySlot records.
    activity_slot = forms.ModelChoiceField(
        queryset=ActivitySlot.objects.none(),
        label="Activity date and time"
    )

    # Customers specify how many people will participate.
    participant_count = forms.IntegerField(
        min_value=1,
        label="Number of participants"
    )

    # Optional code entered by the customer before creating a booking.
    promo_code = forms.CharField(
        max_length=40,
        required=False,
        label="Promo code",
    )

    def __init__(self, *args, activity, **kwargs):

        # Initialise the normal Django form.
        super().__init__(*args, **kwargs)

        # Remember which activity the customer wants to book.
        self.activity = activity

        # Retrieve dates blocked for this activity or all activities.
        blocked_dates = ActivityBlockedDate.objects.filter(
            Q(activity=activity) | Q(activity__isnull=True)
        ).values_list("date", flat=True)

        # Retrieve future, active sessions belonging to this activity.
        slots = ActivitySlot.objects.filter(
            activity=activity,
            is_active=True,
            starts_at__gt=timezone.now()
        ).exclude(
            starts_at__date__in=blocked_dates
        )

        # Count participants in pending or confirmed bookings.
        # Cancelled and completed bookings are not counted,
        # matching the existing ACTIVITIES view.
        slots = slots.annotate(
            booked_places=Sum(
                "reservations__participant_count",
                filter=Q(
                    reservations__booking__status__in=[
                        Booking.Status.PENDING,
                        Booking.Status.CONFIRMED
                    ]
                )
            )
        )

        # Do not display sessions that are already full.
        slots = slots.filter(
            Q(booked_places__isnull=True) |
            Q(booked_places__lt=F("capacity"))
        ).order_by("starts_at")

        # Display the available sessions in the form dropdown.
        self.fields["activity_slot"].queryset = slots

    def clean(self):

        # Run Django's built-in field validation first.
        cleaned_data = super().clean()

        slot = cleaned_data.get("activity_slot")
        participants = cleaned_data.get("participant_count")

        # Continue only when both fields contain valid values.
        if slot is None or participants is None:
            return cleaned_data

        # Check the activity's minimum participants.
        if participants < self.activity.min_participants:
            raise forms.ValidationError(
                f"At least {self.activity.min_participants} "
                "participants are required."
            )

        # Check the activity's maximum participants, if specified.
        if self.activity.max_participants is not None:
            if participants > self.activity.max_participants:
                raise forms.ValidationError(
                    f"Maximum {self.activity.max_participants} "
                    "participants are allowed."
                )

        # Check how many places have already been booked.
        booked_places = slot.reservations.filter(
            booking__status__in=[
                Booking.Status.PENDING,
                Booking.Status.CONFIRMED
            ]
        ).aggregate(
            total=Sum("participant_count")
        )["total"] or 0

        # Calculate the number of places still available.
        available_places = slot.capacity - booked_places

        # Reject bookings exceeding the remaining capacity.
        if participants > available_places:
            raise forms.ValidationError(
                f"Only {available_places} places are available."
            )

        # Return the validated form data.
        return cleaned_data

    def clean_promo_code(self):
        """Validate a code now; its usage is recorded only after payment."""
        code = self.cleaned_data["promo_code"].strip().upper()

        # A blank field means the customer does not want a discount.
        if not code:
            return None

        try:
            promo_code = PromoCode.objects.get(code__iexact=code)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError("This promo code does not exist.")

        now = timezone.now()
        if not promo_code.is_active:
            raise forms.ValidationError("This promo code is not active.")
        if not promo_code.valid_from <= now <= promo_code.valid_until:
            raise forms.ValidationError("This promo code is not valid at this time.")
        if (
            promo_code.max_uses is not None
            and promo_code.uses_count >= promo_code.max_uses
        ):
            raise forms.ValidationError("This promo code has reached its usage limit.")

        return promo_code
