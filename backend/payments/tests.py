
from django.test import TestCase
from django.urls import reverse


class PaymentPageTests(TestCase):
    def test_payment_list_requires_login(self):
        response = self.client.get(reverse("payments:payment_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)
