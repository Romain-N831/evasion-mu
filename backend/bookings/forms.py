
from django import forms
from django.db.models import Sum, Q, F
from django.utils import timezone

from activities.models import ActivitySlot, ActivityBlockedDate
from .models import Booking


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
