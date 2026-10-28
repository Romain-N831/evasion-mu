from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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


class AuthenticationRedirectTests(TestCase):
    def create_user_with_customer(self, *, username, verified=True):
        user = User.objects.create_user(
            username=username,
            password="SafeTestPass123!",
        )
        customer = Customer.objects.create(
            user=user,
            is_verified=verified,
        )
        return user, customer

    def test_successful_verification_redirects_home_and_clears_code(self):
        user, customer = self.create_user_with_customer(
            username="verificationuser",
            verified=False,
        )
        customer.verification_code = "123456"
        customer.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
        customer.save()
        session = self.client.session
        session["pending_verification_user_id"] = user.pk
        session.save()

        response = self.client.post(reverse("users:verify"), {"code": "123456"})

        self.assertRedirects(response, reverse("core:home"))
        customer.refresh_from_db()
        self.assertTrue(customer.is_verified)
        self.assertEqual(customer.verification_code, "")
        self.assertIsNone(customer.verification_code_expires_at)
        self.assertNotIn("pending_verification_user_id", self.client.session)

    def test_verified_user_login_redirects_home_without_next(self):
        self.create_user_with_customer(username="verifiedlogin")

        response = self.client.post(
            reverse("users:login"),
            {"username": "verifiedlogin", "password": "SafeTestPass123!"},
        )

        self.assertRedirects(response, reverse("core:home"))

    def test_login_respects_next_destination(self):
        self.create_user_with_customer(username="nextlogin")
        destination = reverse("users:profile")

        response = self.client.post(
            reverse("users:login"),
            {
                "username": "nextlogin",
                "password": "SafeTestPass123!",
                "next": destination,
            },
        )

        self.assertRedirects(response, destination)

    def test_unverified_user_cannot_log_in(self):
        self.create_user_with_customer(username="unverifiedlogin", verified=False)

        response = self.client.post(
            reverse("users:login"),
            {"username": "unverifiedlogin", "password": "SafeTestPass123!"},
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_user_without_customer_profile_cannot_log_in(self):
        User.objects.create_user(
            username="no-profile",
            password="SafeTestPass123!",
        )

        response = self.client.post(
            reverse("users:login"),
            {"username": "no-profile", "password": "SafeTestPass123!"},
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class BaseNavigationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="navigationuser",
            password="SafeTestPass123!",
        )
        Customer.objects.create(user=self.user, is_verified=True)

    def test_authenticated_navigation_shows_profile_link(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, reverse("users:profile"))
        self.assertContains(response, 'aria-label="My Profile"')
        self.assertNotContains(response, 'href="{}">Login'.format(reverse("users:login")))
        self.assertNotContains(response, 'href="{}">Register'.format(reverse("users:register")))

    def test_anonymous_navigation_shows_login_and_register_links(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, reverse("users:login"))
        self.assertContains(response, reverse("users:register"))
        self.assertNotContains(response, 'aria-label="My Profile"')



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
