from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from activities.models import Activity, ActivitySlot
from bookings.models import Booking, Reservation
from users.models import Customer

from .models import Review


class ReviewEligibilityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="review-customer",
            password="safe-test-password",
        )
        self.customer = Customer.objects.create(user=self.user, is_verified=True)
        self.activity = Activity.objects.create(
            title="Review activity",
            location="Test location",
            current_price=Decimal("100.00"),
        )
        self.url = reverse("add_review", args=[self.activity.pk])

    def test_customer_without_completed_booking_cannot_review(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"rating": 5, "comment": "Great"})

        self.assertRedirects(response, reverse("activity_reviews", args=[self.activity.pk]))
        self.assertEqual(Review.objects.count(), 0)

    def test_completed_booking_allows_one_review_only(self):
        slot = ActivitySlot.objects.create(
            activity=self.activity,
            starts_at=timezone.now() - timedelta(days=1),
            capacity=10,
        )
        booking = Booking.objects.create(
            customer=self.customer,
            total_amount=Decimal("100.00"),
            status=Booking.Status.COMPLETED,
        )
        Reservation.objects.create(
            booking=booking,
            activity_slot=slot,
            participant_count=1,
            unit_price=Decimal("100.00"),
        )

        self.client.force_login(self.user)
        first_response = self.client.post(
            self.url,
            {"rating": 5, "comment": "Great"},
        )
        second_response = self.client.post(
            self.url,
            {"rating": 4, "comment": "Still great"},
        )

        self.assertRedirects(first_response, reverse("activity_reviews", args=[self.activity.pk]))
        self.assertRedirects(second_response, reverse("activity_reviews", args=[self.activity.pk]))
        self.assertEqual(Review.objects.count(), 1)
