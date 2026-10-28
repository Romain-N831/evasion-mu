import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.views.decorators.http import require_http_methods


from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from bookings.models import Booking
from payments.models import Payment

from .forms import CustomerProfileForm, RegistrationForm
from .models import Customer, CustomerActivityLog



def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Create the customer profile if it does not exist yet.
            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    "phone_number": form.cleaned_data["phone_number"],
                    "contact_preference": form.cleaned_data["contact_preference"],
                },
            )

            code = f"{secrets.randbelow(1_000_000):06d}"

            customer.verification_code = code
            customer.verification_code_expires_at = (
                timezone.now() + timedelta(minutes=10)
            )
            customer.is_verified = False
            customer.save()

            send_mail(
                subject="Verify your Evasion.mu account",
                message=(
                    f"Hello {user.first_name or user.username},\n\n"
                    f"Your Evasion.mu verification code is: {code}\n\n"
                    "This code expires in 10 minutes."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Your account was created. Check the development terminal "
                "for your email verification code."
            )
            request.session["pending_verification_user_id"] = user.pk
            return redirect("users:verify_email")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})



@require_http_methods(["GET", "POST"])
def verify_email(request):
    user_id = request.session.get("pending_verification_user_id")

    if not user_id:
        messages.info(request, "Please register before verifying your email.")
        return redirect("users:register")

    User = get_user_model()

    try:
        user = User.objects.get(pk=user_id, is_active=False)
        customer = user.customer_profile
    except (User.DoesNotExist, Customer.DoesNotExist):
        request.session.pop("pending_verification_user_id", None)
        messages.error(request, "We could not find your pending account.")
        return redirect("users:register")

    if request.method == "POST":
        submitted_code = request.POST.get("verification_code", "").strip()

        if (
            customer.verification_code
            and secrets.compare_digest(
                submitted_code, customer.verification_code
            )
            and customer.verification_code_expires_at
            and timezone.now() <= customer.verification_code_expires_at
        ):
            customer.is_verified = True
            customer.verification_code = ""
            customer.verification_code_expires_at = None
            customer.save()

            user.is_active = True
            user.save(update_fields=["is_active"])

            request.session.pop("pending_verification_user_id", None)
            messages.success(
                request,
                "Your email is verified! You can now log in."
            )
            return redirect("users:login")

        messages.error(
            request,
            "The code is invalid or expired. Please register again for a new code."
        )

    return render(request, "users/verify_email.html")



class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("users:profile")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("home")


@login_required
def profile(request):
    with transaction.atomic():
        customer, _ = Customer.objects.get_or_create(
            user=request.user
        )

    if request.method == "POST":
        form = CustomerProfileForm(
            request.POST,
            instance=customer,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            CustomerActivityLog.objects.create(
                customer=customer,
                action="PROFILE_UPDATED",
            )

            messages.success(
                request,
                "Your profile has been updated."
            )
            return redirect("users:profile")
    else:
        form = CustomerProfileForm(
            instance=customer,
            user=request.user,
        )

    bookings = Booking.objects.filter(
        customer=customer
    ).order_by("-booking_date")[:5]

    payments = Payment.objects.filter(
        booking__customer=customer
    ).order_by("-payment_date")[:5]

    return render(
        request,
        "users/profile.html",
        {
            "form": form,
            "customer": customer,
            "recent_bookings": bookings,
            "recent_payments": payments,
        },
    )


@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            messages.success(
                request,
                "Your password has been changed."
            )
            return redirect("users:profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(
        request,
        "users/password_change.html",
        {"form": form},
    )
