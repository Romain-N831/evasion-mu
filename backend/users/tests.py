
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import Customer

User = get_user_model()


class UserRegistrationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_registration_creates_user_and_customer(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "testuser123",
                "first_name": "Test",
                "last_name": "User",
                "email": "testuser123@example.com",
                "phone_number": "5551234",
                "contact_preference": Customer.ContactPreference.EMAIL,
                "password1": "SafeTestPass123!",
                "password2": "SafeTestPass123!",
            },
        )

        self.assertTrue(
            User.objects.filter(username="testuser123").exists()
        )
        self.assertTrue(
            Customer.objects.filter(
                user__username="testuser123"
            ).exists()
        )
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)
