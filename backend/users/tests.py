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

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="SafeTestPass123!",
        )

        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "EXISTING@example.com",
                "phone_number": "",
                "contact_preference": Customer.ContactPreference.EMAIL,
                "password1": "SafeTestPass123!",
                "password2": "SafeTestPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            first_name="Test",
            last_name="User",
            email="profile@example.com",
            password="SafeTestPass123!",
        )
        self.customer = Customer.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/users/login/", response.url)

    def test_profile_page_loads(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_can_be_updated(self):
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com",
                "phone_number": "5559876",
                "contact_preference": Customer.ContactPreference.SMS,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.customer.refresh_from_db()

        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.customer.phone_number, "5559876")
        self.assertEqual(
            self.customer.contact_preference,
            Customer.ContactPreference.SMS,
        )

    def test_profile_rejects_another_users_email(self):
        User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="SafeTestPass123!",
        )

        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": "another@example.com",
                "phone_number": self.customer.phone_number,
                "contact_preference": self.customer.contact_preference,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "profile@example.com")



class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="passworduser",
            password="OldSafePass123!",
        )
        Customer.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_password_change_page_loads(self):
        response = self.client.get(reverse("users:password_change"))
        self.assertEqual(response.status_code, 200)

    def test_password_can_be_changed(self):
        response = self.client.post(
            reverse("users:password_change"),
            {
                "old_password": "OldSafePass123!",
                "new_password1": "NewSafePass456!",
                "new_password2": "NewSafePass456!",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("NewSafePass456!")
        )

    def test_incorrect_current_password_is_rejected(self):
        response = self.client.post(
            reverse("users:password_change"),
            {
                "old_password": "WrongPassword123!",
                "new_password1": "NewSafePass456!",
                "new_password2": "NewSafePass456!",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("OldSafePass123!")
        )
