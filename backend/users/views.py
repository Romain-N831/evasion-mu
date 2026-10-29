
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from bookings.models import Booking
from payments.models import Payment

from .forms import (
    CustomerProfileForm,
    RegistrationForm,
    VerificationCodeForm,
)
from .models import Customer, CustomerActivityLog
from .utils import send_verification_email


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # Create the user and customer profile.
            user = form.save()
            customer = user.customer_profile

            # Remember which account is awaiting verification.
            request.session["pending_verification_user_id"] = user.pk

            # Send the verification email.
            try:
                send_verification_email(customer)
            except Exception:
                messages.error(
                    request,
                    "Your account was created, but we could not send "
                    "the verification email. Please try requesting a "
                    "new code.",
                )
                return redirect("users:verify")

            messages.success(
                request,
                "Account created. Check your email for your "
                "verification code.",
            )
            return redirect("users:verify")

    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


def verify_account(request):
    user_id = request.session.get("pending_verification_user_id")

    if not user_id:
        messages.info(
            request,
            "Please register to verify your account.",
        )
        return redirect("users:register")

    try:
        customer = Customer.objects.select_related("user").get(
            user_id=user_id
        )
    except Customer.DoesNotExist:
        request.session.pop("pending_verification_user_id", None)
        messages.error(request, "We could not find that account.")
        return redirect("users:register")

    if customer.is_verified:
        request.session.pop("pending_verification_user_id", None)
        messages.info(request, "Your account is already verified.")
        return redirect("users:login")

    if request.method == "POST":
        form = VerificationCodeForm(request.POST)

        if form.is_valid():
            submitted_code = form.cleaned_data["code"]

            if (
                customer.verification_code == submitted_code
                and customer.verification_code_expires_at
                and customer.verification_code_expires_at > timezone.now()
            ):
                customer.is_verified = True
                customer.verification_code = ""
                customer.verification_code_expires_at = None
                customer.save(
                    update_fields=[
                        "is_verified",
                        "verification_code",
                        "verification_code_expires_at",
                        "updated_at",
                    ]
                )

                # Activate the account after successful verification.
                user = customer.user
                user.is_active = True
                user.save(update_fields=["is_active"])

                request.session.pop(
                    "pending_verification_user_id", None
                )

                messages.success(
                    request,
                    "Your account is verified. You can now log in.",
                )
                return redirect("home")

            form.add_error(
                "code",
                "The code is incorrect or has expired. Please try again.",
            )
    else:
        form = VerificationCodeForm()

    return render(
        request,
        "users/verify_account.html",
        {
            "form": form,
            "customer": customer,
        },
    )


@require_POST
def resend_verification_code(request):
    user_id = request.session.get("pending_verification_user_id")

    if not user_id:
        messages.info(
            request,
            "Please register or start verification first.",
        )
        return redirect("users:register")

    try:
        customer = Customer.objects.select_related("user").get(
            user_id=user_id
        )
    except Customer.DoesNotExist:
        request.session.pop("pending_verification_user_id", None)
        messages.error(request, "We could not find that account.")
        return redirect("users:register")

    if customer.is_verified:
        request.session.pop("pending_verification_user_id", None)
        messages.info(request, "Your account is already verified.")
        return redirect("users:login")

    try:
        send_verification_email(customer)
    except Exception:
        messages.error(
            request,
            "We could not send a new verification email. "
            "Please try again later.",
        )
    else:
        messages.success(
            request,
            "A new verification code has been sent to your email.",
        )

    return redirect("users:verify")


def verify_account(request):
    user_id = request.session.get("pending_verification_user_id")

    if not user_id:
        messages.info(
            request,
            "Please register to verify your account.",
        )
        return redirect("users:register")

    try:
        customer = Customer.objects.select_related("user").get(
            user_id=user_id
        )
    except Customer.DoesNotExist:
        request.session.pop("pending_verification_user_id", None)
        messages.error(request, "We could not find that account.")
        return redirect("users:register")

    if customer.is_verified:
        request.session.pop("pending_verification_user_id", None)
        messages.info(request, "Your account is already verified.")
        return redirect("users:login")

    if request.method == "POST":
        form = VerificationCodeForm(request.POST)

        if form.is_valid():
            if (
                customer.verification_code == form.cleaned_data["code"]
                and customer.verification_code_expires_at
                and customer.verification_code_expires_at > timezone.now()
            ):
                customer.is_verified = True
                customer.verification_code = ""
                customer.verification_code_expires_at = None
                customer.save(
                    update_fields=[
                        "is_verified",
                        "verification_code",
                        "verification_code_expires_at",
                        "updated_at",
                    ]
                )

                request.session.pop("pending_verification_user_id", None)

                messages.success(
                    request,
                    "Your account is verified. You can now log in.",
                )
                return redirect("core:home")

            form.add_error(
                "code",
                "The code is incorrect or has expired. Please try again.",
            )
    else:
        form = VerificationCodeForm()

    return render(
        request,
        "users/verify_account.html",
        {
            "form": form,
            "customer": customer,
        },
    )


class UserLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("core:home")

    def form_valid(self, form):
        user = form.get_user()

        try:
            customer = user.customer_profile
        except Customer.DoesNotExist:
            messages.error(
                self.request,
                "This account does not have a customer profile. "
                "Please contact support.",
            )
            return redirect("users:login")

        if not customer.is_verified:
            messages.error(
                self.request,
                "Please verify your account before logging in.",
            )
            return redirect("users:login")

        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


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
                "Your profile has been updated.",
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
                "Your password has been changed.",
            )
            return redirect("users:profile")

    else:
        form = PasswordChangeForm(user=request.user)

    return render(
        request,
        "users/password_change.html",
        {"form": form},
    )
