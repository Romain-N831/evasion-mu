from django.conf import settings
from django.db import models


class Customer(models.Model):
    # Profile for Django's built-in auth user; avoids changing
    # AUTH_USER_MODEL after the initial migrations have been applied.
    class ContactPreference(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        SMS = "SMS", "SMS"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    phone_number = models.CharField(max_length=25, blank=True)
    contact_preference = models.CharField(
        max_length=10,
        choices=ContactPreference.choices,
        default=ContactPreference.EMAIL,
    )
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(
        max_length=6,
        blank=True,
        default="",
    )
    verification_code_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            self.user.get_full_name().strip()
            or self.user.get_username()
        )



class CustomerActivityLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer} — {self.action}"
