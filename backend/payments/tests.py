
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking, PromoCode
from users.models import Customer


class PaymentPageTests(TestCase):
    def test_payment_list_requires_login(self):
        response = self.client.get(reverse("payments:payment_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_successful_demo_checkout_redirects_to_payment_detail(self):
        """A pending booking completes simulated checkout and opens its receipt."""
        user = get_user_model().objects.create_user(
            username="payment-customer",
            password="safe-test-password",
        )
        customer = Customer.objects.create(user=user, is_verified=True)
        booking = Booking.objects.create(
            customer=customer,
            total_amount=Decimal("1250.00"),
        )

        self.client.force_login(user)
        response = self.client.post(
            reverse("payments:checkout", args=[booking.pk]),
        )
        payment = booking.payments.get()

        self.assertRedirects(
            response,
            reverse("payments:payment_detail", args=[payment.pk]),
        )
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CONFIRMED)

    def test_confirmed_booking_cannot_be_paid_twice(self):
        """A successful payment changes the status, blocking a second payment."""
        user = get_user_model().objects.create_user(
            username="repeat-payment-customer",
            password="safe-test-password",
        )
        customer = Customer.objects.create(user=user, is_verified=True)
        booking = Booking.objects.create(
            customer=customer,
            total_amount=Decimal("750.00"),
        )

        self.client.force_login(user)
        checkout_url = reverse("payments:checkout", args=[booking.pk])
        self.client.post(checkout_url)
        second_response = self.client.post(checkout_url)

        self.assertRedirects(
            second_response,
            reverse("bookings:booking-detail", args=[booking.pk]),
        )
        self.assertEqual(booking.payments.count(), 1)

    def test_successful_demo_payment_consumes_promo_code_once(self):
        """Promo-code usage is recorded after one successful demo payment."""
        user = get_user_model().objects.create_user(
            username="promo-payment-customer",
            password="safe-test-password",
        )
        customer = Customer.objects.create(user=user, is_verified=True)
        promo_code = PromoCode.objects.create(
            code="PAYMENTPROMO",
            discount_type=PromoCode.DiscountType.FIXED,
            discount_value=Decimal("20.00"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            max_uses=1,
        )
        booking = Booking.objects.create(
            customer=customer,
            total_amount=Decimal("100.00"),
            promo_code=promo_code,
            discount_amount=Decimal("20.00"),
        )

        self.client.force_login(user)
        self.client.post(reverse("payments:checkout", args=[booking.pk]))
        self.client.post(reverse("payments:checkout", args=[booking.pk]))

        promo_code.refresh_from_db()
        self.assertEqual(promo_code.uses_count, 1)
