
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
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
        return redirect("payments:detail", payment_id=payment.pk)

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
