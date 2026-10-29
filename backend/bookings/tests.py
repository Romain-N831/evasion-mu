from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from activities.models import Activity, ActivitySlot
from hotels.models import Hotel, RoomAvailability, RoomType
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
        self.assertEqual(self.booking.status, Booking.Status.PENDING)

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


class HotelBookingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="hotel-customer", password="safe-test-password")
        self.customer = Customer.objects.create(user=self.user, is_verified=True)
        self.hotel = Hotel.objects.create(name="Booking Hotel")
        self.room_type = RoomType.objects.create(
            hotel=self.hotel, name="Ocean Suite", max_occupancy=2,
            price_per_night=Decimal("1500.00"), total_rooms=5,
        )
        self.check_in = timezone.localdate() + timedelta(days=3)
        self.check_out = self.check_in + timedelta(days=2)
        self.availability = [
            RoomAvailability.objects.create(room_type=self.room_type, date=self.check_in + timedelta(days=offset), available_rooms=4)
            for offset in range(2)
        ]
        self.url = reverse("bookings:book-hotel", args=[self.hotel.pk, self.room_type.pk])

    def post(self, **overrides):
        data = {
            "check_in": self.check_in.isoformat(), "check_out": self.check_out.isoformat(),
            "rooms_count": 2, "guests_count": 3,
        }
        data.update(overrides)
        return self.client.post(self.url, data)

    def test_successful_reservation_calculates_total_and_decrements_every_night_once(self):
        self.client.force_login(self.user)
        response = self.post()
        booking = Booking.objects.get()
        reservation = booking.hotel_reservations.get()
        self.assertRedirects(response, reverse("bookings:booking-detail", args=[booking.pk]))
        self.assertEqual(booking.total_amount, Decimal("6000.00"))
        self.assertEqual(reservation.price_per_night, Decimal("1500.00"))
        self.assertEqual(reservation.guests_count, 3)
        for row in self.availability:
            row.refresh_from_db()
            self.assertEqual(row.available_rooms, 2)

    def test_invalid_dates_do_not_create_booking(self):
        self.client.force_login(self.user)
        response = self.post(check_out=self.check_in.isoformat())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Check-out must be after check-in.")
        response = self.post(check_in=(timezone.localdate() - timedelta(days=1)).isoformat())
        self.assertContains(response, "Check-in cannot be in the past.")
        self.assertFalse(Booking.objects.exists())

    def test_inactive_hotel_or_room_type_is_not_bookable(self):
        self.client.force_login(self.user)
        self.hotel.is_active = False
        self.hotel.save(update_fields=["is_active"])
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.hotel.is_active = True
        self.hotel.save(update_fields=["is_active"])
        self.room_type.is_active = False
        self.room_type.save(update_fields=["is_active"])
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_occupancy_and_missing_or_insufficient_inventory_are_rejected(self):
        self.client.force_login(self.user)
        response = self.post(guests_count=5)
        self.assertContains(response, "accommodates at most")
        RoomAvailability.objects.filter(pk=self.availability[1].pk).delete()
        response = self.post()
        self.assertContains(response, "Availability has not been configured")
        self.availability[1] = RoomAvailability.objects.create(room_type=self.room_type, date=self.check_in + timedelta(days=1), available_rooms=1)
        response = self.post()
        self.assertContains(response, "not enough rooms")
        self.assertFalse(Booking.objects.exists())

    def test_cancellation_restores_inventory_once(self):
        self.client.force_login(self.user)
        self.post()
        booking = Booking.objects.get()
        cancel_url = reverse("bookings:request-cancellation", args=[booking.pk])
        self.client.post(cancel_url)
        self.client.post(cancel_url)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)
        self.assertTrue(booking.hotel_reservations.get().inventory_released)
        for row in self.availability:
            row.refresh_from_db()
            self.assertEqual(row.available_rooms, 4)

    def test_confirmed_hotel_cancellation_creates_a_demo_refund(self):
        from payments.models import Payment
        self.client.force_login(self.user)
        self.post()
        booking = Booking.objects.get()
        Payment.objects.create(
            booking=booking, amount_paid=booking.total_amount,
            payment_method=Payment.Method.DEMO, status=Payment.Status.SUCCESSFUL,
            transaction_type=Payment.TransactionType.PAYMENT,
            transaction_reference="DEMO-PAID-HOTEL",
        )
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=["status"])
        self.client.post(reverse("bookings:request-cancellation", args=[booking.pk]))
        self.assertTrue(booking.payments.filter(
            transaction_type=Payment.TransactionType.REFUND,
            status=Payment.Status.REFUNDED,
        ).exists())

    def test_hotel_booking_uses_the_existing_demo_checkout(self):
        self.client.force_login(self.user)
        self.post()
        booking = Booking.objects.get()
        response = self.client.post(reverse("payments:checkout", args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)
        self.assertRedirects(response, reverse("payments:payment_detail", args=[booking.payments.get().pk]))
        for row in self.availability:
            row.refresh_from_db()
            self.assertEqual(row.available_rooms, 2)

    def test_login_and_customer_ownership_are_enforced(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.user)
        self.post()
        booking = Booking.objects.get()
        other = get_user_model().objects.create_user(username="hotel-other", password="safe-test-password")
        Customer.objects.create(user=other, is_verified=True)
        self.client.force_login(other)
        self.assertEqual(self.client.get(reverse("bookings:booking-detail", args=[booking.pk])).status_code, 404)

    def test_failed_reservation_creation_rolls_back_inventory_and_booking(self):
        self.client.force_login(self.user)
        with patch("bookings.views.HotelReservation.objects.create", side_effect=RuntimeError("database write failed")):
            with self.assertRaises(RuntimeError):
                self.post()
        self.assertFalse(Booking.objects.exists())
        for row in self.availability:
            row.refresh_from_db()
            self.assertEqual(row.available_rooms, 4)
