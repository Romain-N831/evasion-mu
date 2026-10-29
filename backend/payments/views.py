
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking, PromoCode
from .models import Payment


@login_required
def payment_list(request):
    payments = Payment.objects.filter(
        booking__customer__user=request.user
    ).select_related("booking")

    return render(
        request,
        "payments/payment_list.html",
        {"payments": payments},
    )


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("customer"),
        pk=booking_id,
        customer__user=request.user,
    )

    if booking.status != Booking.Status.PENDING:
        messages.info(request, "This booking is not awaiting payment.")
        return redirect("bookings:booking-detail", pk=booking.pk)

    if request.method == "POST":
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(pk=booking.pk)

            if booking.status != Booking.Status.PENDING:
                messages.info(request, "This booking has already been processed.")
                return redirect("bookings:booking-detail", pk=booking.pk)

            # A promo code is consumed only when this simulated payment succeeds.
            # Refresh it under a lock so two checkouts cannot exceed max_uses.
            if booking.promo_code_id:
                promo_code = PromoCode.objects.select_for_update().get(
                    pk=booking.promo_code_id
                )
                if (
                    not promo_code.is_active
                    or not promo_code.valid_from <= timezone.now() <= promo_code.valid_until
                    or (
                        promo_code.max_uses is not None
                        and promo_code.uses_count >= promo_code.max_uses
                    )
                ):
                    messages.error(
                        request,
                        "The promo code on this booking is no longer available."
                    )
                    return redirect("bookings:booking-detail", pk=booking.pk)

                promo_code.uses_count += 1
                promo_code.save(update_fields=["uses_count"])

            payment = Payment.objects.create(
                booking=booking,
                amount_paid=booking.total_amount,
                payment_method=Payment.Method.DEMO,
                status=Payment.Status.SUCCESSFUL,
                transaction_type=Payment.TransactionType.PAYMENT,
                transaction_reference=f"DEMO-{uuid.uuid4().hex[:12].upper()}",
            )

            booking.status = Booking.Status.CONFIRMED
            booking.save(update_fields=["status"])

        messages.success(request, "Demo payment successful! No real money was charged.")
        # The URL pattern is named "payment_detail" in payments/urls.py.
        # Use that exact name so a successful demo checkout reaches its receipt.
        return redirect("payments:payment_detail", payment_id=payment.pk)

    return render(
        request,
        "payments/checkout.html",
        {"booking": booking},
    )


@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(
        Payment.objects.select_related("booking"),
        pk=payment_id,
        booking__customer__user=request.user,
    )

    return render(
        request,
        "payments/payment_detail.html",
        {"payment": payment},
    )
