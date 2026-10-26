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
    if request.user.is_authenticated:
        return redirect("users:profile")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "Your Evasion.mu account has been created."
            )
            return redirect("users:profile")
    else:
        form = RegistrationForm()

    return render(
        request,
        "users/register.html",
        {"form": form},
    )


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
