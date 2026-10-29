from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from activities.models import Activity, ActivitySlot
from users.models import Customer

from .models import Booking, PromoCode


class ActivityBookingPromoCodeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="booking-customer",
            password="safe-test-password",
        )
        Customer.objects.create(user=self.user, is_verified=True)
        self.activity = Activity.objects.create(
            title="Test activity",
            location="Test location",
            current_price=Decimal("100.00"),
        )
        self.slot = ActivitySlot.objects.create(
            activity=self.activity,
            starts_at=timezone.now() + timedelta(days=2),
            capacity=10,
        )
        self.valid_from = timezone.now() - timedelta(days=1)
        self.valid_until = timezone.now() + timedelta(days=1)

    def test_percentage_promo_reduces_booking_total(self):
        PromoCode.objects.create(
            code="SAVE10",
            discount_type=PromoCode.DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            valid_from=self.valid_from,
            valid_until=self.valid_until,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("bookings:book-activity", args=[self.activity.pk]),
            {"activity_slot": self.slot.pk, "participant_count": 2, "promo_code": "save10"},
        )

        booking = Booking.objects.get()
        self.assertRedirects(
            response,
            reverse("bookings:booking-detail", args=[booking.pk]),
        )
        self.assertEqual(booking.discount_amount, Decimal("20.00"))
        self.assertEqual(booking.total_amount, Decimal("180.00"))

    def test_inactive_promo_does_not_create_booking(self):
        PromoCode.objects.create(
            code="INACTIVE",
            discount_type=PromoCode.DiscountType.FIXED,
            discount_value=Decimal("10.00"),
            valid_from=self.valid_from,
            valid_until=self.valid_until,
            is_active=False,
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse("bookings:book-activity", args=[self.activity.pk]),
            {"activity_slot": self.slot.pk, "participant_count": 1, "promo_code": "inactive"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This promo code is not active.")
        self.assertEqual(Booking.objects.count(), 0)


class CancellationRequestTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cancellation-customer",
            password="safe-test-password",
        )
        self.customer = Customer.objects.create(user=self.user, is_verified=True)
        self.booking = Booking.objects.create(
            customer=self.customer,
            total_amount=Decimal("500.00"),
        )

    def test_customer_can_request_cancellation_for_own_pending_booking(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("bookings:request-cancellation", args=[self.booking.pk]),
            {"cancellation_reason": "My travel plans changed."},
        )

        self.assertRedirects(
            response,
            reverse("bookings:booking-detail", args=[self.booking.pk]),
        )
        self.booking.refresh_from_db()
        self.assertIsNotNone(self.booking.cancellation_requested_at)
        self.assertEqual(self.booking.cancellation_reason, "My travel plans changed.")

    def test_customer_cannot_request_cancellation_for_another_booking(self):
        other_user = get_user_model().objects.create_user(
            username="other-customer",
            password="safe-test-password",
        )
        Customer.objects.create(user=other_user, is_verified=True)

        self.client.force_login(other_user)
        response = self.client.post(
            reverse("bookings:request-cancellation", args=[self.booking.pk]),
        )

        self.assertEqual(response.status_code, 404)
