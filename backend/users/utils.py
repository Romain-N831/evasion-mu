import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

VERIFICATION_CODE_EXPIRY_MINUTES = 10


def generate_verification_code():
    """Generate a cryptographically secure, six-digit verification code."""
    return f"{secrets.randbelow(1_000_000):06d}"


def send_verification_email(customer):
    """Generate, save, and email a verification code to the customer."""
    if customer.is_verified:
        return

    code = generate_verification_code()

    customer.verification_code = code
    customer.verification_code_expires_at = (
        timezone.now()
        + timedelta(minutes=VERIFICATION_CODE_EXPIRY_MINUTES)
    )

    customer.save(
        update_fields=[
            "verification_code",
            "verification_code_expires_at",
            "updated_at",
        ]
    )

    send_mail(
        subject="Verify your Evasion.mu account",
        message=(
            f"Hello {customer.user.first_name or customer.user.username},\n\n"
            f"Your Evasion.mu verification code is: {code}\n\n"
            f"This code expires in {VERIFICATION_CODE_EXPIRY_MINUTES} minutes.\n\n"
            "If you did not create this account, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer.user.email],
        fail_silently=False,
    )
