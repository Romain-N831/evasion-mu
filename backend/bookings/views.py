
# Django imports
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.views import generic
from django.db import transaction
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError
from django.utils import timezone

# Models from other apps
from activities.models import Activity, ActivitySlot, ActivityBlockedDate
from users.models import Customer

# Our BOOKINGS app
from .models import Booking, PromoCode, Reservation
from .forms import ActivityBookingForm

# Display the bookings belonging to the logged-in customer.
# LoginRequiredMixin must appear before generic.ListView.
class BookingListView(LoginRequiredMixin, generic.ListView):

    # Tell Django which model this page displays.
    model = Booking

    # Specify the HTML template used for this page.
    template_name = 'bookings/booking_list.html'

    # The template will access the results using "booking_list".
    context_object_name = 'booking_list'


    # Decide which database records this customer may see.
    def get_queryset(self):

        # Follow Booking -> Customer -> User.
        # Only include bookings linked to the currently logged-in user.
        # A user without a Customer profile receives an empty list.
        return Booking.objects.filter(
            customer__user=self.request.user
        ).order_by('-booking_date', '-pk')


# Display one booking and its associated reservations.
class BookingDetailView(LoginRequiredMixin, generic.DetailView):

    model = Booking
    template_name = 'bookings/booking_detail.html'

    # The template will access this single record using "booking".
    context_object_name = 'booking'


    def get_queryset(self):

        # Restrict the available records BEFORE Django looks up the URL's ID.
        # This prevents someone from viewing another customer's booking
        # simply by changing the number in the address bar.
        return Booking.objects.filter(
            customer__user=self.request.user
        )


@login_required
def request_cancellation(request, pk):
    """Record a simple customer cancellation request for staff review."""
    booking = get_object_or_404(
        Booking,
        pk=pk,
        customer__user=request.user,
    )

    # Cancellation changes data, so it must be submitted using POST.
    if request.method != "POST":
        return redirect("bookings:booking-detail", pk=booking.pk)

    # Only unpaid/active bookings can be requested for cancellation.
    if booking.status not in (Booking.Status.PENDING, Booking.Status.CONFIRMED):
        messages.error(request, "This booking is not eligible for cancellation.")
        return redirect("bookings:booking-detail", pk=booking.pk)

    if booking.cancellation_requested_at:
        messages.info(request, "A cancellation request is already awaiting review.")
        return redirect("bookings:booking-detail", pk=booking.pk)

    booking.cancellation_requested_at = timezone.now()
    booking.cancellation_reason = request.POST.get("cancellation_reason", "").strip()
    booking.save(update_fields=["cancellation_requested_at", "cancellation_reason"])

    messages.success(request, "Your cancellation request has been sent for staff review.")
    return redirect("bookings:booking-detail", pk=booking.pk)
        

# Only logged-in customers can book activities.
@login_required
def book_activity(request, activity_id):

    # Find the selected activity.
    # Return a 404 page if the activity does not exist or is inactive.
    activity = get_object_or_404(
        Activity,
        pk=activity_id,
        is_active=True
    )

    # Check that the logged-in user has a Customer profile.
    customer = Customer.objects.filter(
        user=request.user
    ).first()

    # Do not allow users without a Customer profile to book.
    if customer is None:
        return HttpResponseForbidden(
            "You need a Customer profile to make a booking."
        )

    # If the customer submits the form.
    if request.method == "POST":

        # Bind the submitted information to our booking form.
        form = ActivityBookingForm(
            request.POST,
            activity=activity
        )

        # Proceed only when the form data is valid.
        if form.is_valid():

            # Retrieve the validated slot and participant count.
            selected_slot = form.cleaned_data["activity_slot"]
            participants = form.cleaned_data["participant_count"]

            try:
                # Both database records must be saved together.
                # If anything fails, neither record is saved.
                with transaction.atomic():

                    # Lock the selected slot while checking capacity.
                    # This prevents two booking requests from
                    # reserving the same remaining places simultaneously.
                    slot = ActivitySlot.objects.select_for_update().select_related(
                        "activity"
                    ).filter(
                        pk=selected_slot.pk
                    ).first()

                    # Check that the slot still exists and is usable.
                    if (
                        slot is None
                        or slot.activity_id != activity.pk
                        or not slot.is_active
                        or not slot.activity.is_active
                    ):
                        raise ValidationError(
                            "This activity slot is no longer available."
                        )

                    # Prevent booking a session that has already passed.
                    if slot.starts_at <= timezone.now():
                        raise ValidationError(
                            "You cannot book a past activity slot."
                        )

                    # Check blocked dates for this activity
                    # and dates blocked for all activities.
                    slot_date = timezone.localtime(
                        slot.starts_at
                    ).date()

                    blocked = ActivityBlockedDate.objects.filter(
                        Q(activity=activity) |
                        Q(activity__isnull=True),
                        date=slot_date
                    ).exists()

                    if blocked:
                        raise ValidationError(
                            "Bookings are not allowed on this date."
                        )

                    # Count places already reserved in this slot.
                    # Pending and confirmed bookings use capacity.
                    booked_places = Reservation.objects.filter(
                        activity_slot=slot,
                        booking__status__in=[
                            Booking.Status.PENDING,
                            Booking.Status.CONFIRMED
                        ]
                    ).aggregate(
                        total=Sum("participant_count")
                    )["total"] or 0

                    # Calculate the remaining places.
                    available_places = slot.capacity - booked_places

                    # Check capacity again immediately before saving.
                    if participants > available_places:
                        raise ValidationError(
                            f"Only {available_places} places remain."
                        )

                    # Recheck participant limits before saving.
                    if participants < slot.activity.min_participants:
                        raise ValidationError(
                            "The participant count is below the minimum."
                        )

                    if (
                        slot.activity.max_participants is not None
                        and participants > slot.activity.max_participants
                    ):
                        raise ValidationError(
                            "The participant count exceeds the maximum."
                        )

                    # Save the current price and calculate the booking total.
                    unit_price = slot.activity.current_price
                    subtotal = unit_price * participants

                    # Re-lock and re-check the optional promo code just before
                    # saving. This prevents an expired or exhausted code being
                    # accepted after the customer loaded the form.
                    promo_code = form.cleaned_data["promo_code"]
                    discount_amount = 0
                    if promo_code is not None:
                        promo_code = PromoCode.objects.select_for_update().get(
                            pk=promo_code.pk
                        )
                        now = timezone.now()
                        if (
                            not promo_code.is_active
                            or not promo_code.valid_from <= now <= promo_code.valid_until
                            or (
                                promo_code.max_uses is not None
                                and promo_code.uses_count >= promo_code.max_uses
                            )
                        ):
                            raise ValidationError(
                                "This promo code is no longer available."
                            )

                        # Percentage codes use the activity subtotal. Fixed codes
                        # never reduce the final booking total below zero.
                        if promo_code.discount_type == PromoCode.DiscountType.PERCENTAGE:
                            discount_amount = (
                                subtotal * promo_code.discount_value / 100
                            )
                        else:
                            discount_amount = promo_code.discount_value
                        discount_amount = min(discount_amount, subtotal)

                    total_price = subtotal - discount_amount

                    # Create the main Booking record.
                    # Status defaults to PENDING in the existing model.
                    booking = Booking.objects.create(
                        customer=customer,
                        total_amount=total_price,
                        promo_code=promo_code,
                        discount_amount=discount_amount,
                    )

                    # Create the related activity Reservation record.
                    Reservation.objects.create(
                        booking=booking,
                        activity_slot=slot,
                        participant_count=participants,
                        unit_price=unit_price
                    )

                # After a successful transaction, redirect to
                # the existing booking detail page.
                return redirect(
                    'bookings:booking-detail',
                    pk=booking.pk
                )

            # Show a friendly error if availability changed.
            except ValidationError as error:
                form.add_error(None, error)

    else:
        # For a GET request, display an empty booking form.
        form = ActivityBookingForm(activity=activity)

    # Send the activity and form to the HTML template.
    context = {
        "activity": activity,
        "form": form,
    }

    return render(
        request,
        "bookings/activity_booking.html",
        context
    )
        
# Create your views here.
