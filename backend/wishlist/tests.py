from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from activities.models import Activity
from users.models import Customer

from .models import WishlistItem


class WishlistTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="wishlist-customer",
            password="safe-test-password",
        )
        Customer.objects.create(user=self.user, is_verified=True)
        self.activity = Activity.objects.create(
            title="Wishlist activity",
            location="Test location",
            current_price=Decimal("100.00"),
        )

    def test_customer_can_add_an_activity_once(self):
        self.client.force_login(self.user)
        add_url = reverse("wishlist:add")

        self.client.post(add_url, {"activity_id": self.activity.pk})
        self.client.post(add_url, {"activity_id": self.activity.pk})

        self.assertEqual(WishlistItem.objects.count(), 1)

    def test_customer_cannot_remove_another_customers_item(self):
        self.client.force_login(self.user)
        self.client.post(reverse("wishlist:add"), {"activity_id": self.activity.pk})
        item = WishlistItem.objects.get()

        other_user = get_user_model().objects.create_user(
            username="other-wishlist-customer",
            password="safe-test-password",
        )
        Customer.objects.create(user=other_user, is_verified=True)
        self.client.force_login(other_user)

        response = self.client.post(reverse("wishlist:remove", args=[item.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(WishlistItem.objects.filter(pk=item.pk).exists())
