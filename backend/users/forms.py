from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Customer

User = get_user_model()


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=25, required=False)

    contact_preference = forms.ChoiceField(
        choices=Customer.ContactPreference.choices,
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "contact_preference",
        )

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"].strip()

        if not first_name:
            raise forms.ValidationError("First name is required.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"].strip()

        if not last_name:
            raise forms.ValidationError("Last name is required.")

        return last_name

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            self.save_m2m()

            Customer.objects.create(
                user=user,
                phone_number=self.cleaned_data.get(
                    "phone_number", ""
                ).strip(),
                contact_preference=self.cleaned_data[
                    "contact_preference"
                ],
            )

        return user


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Customer
        fields = ("phone_number", "contact_preference")

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"].strip()

        if not first_name:
            raise forms.ValidationError("First name is required.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"].strip()

        if not last_name:
            raise forms.ValidationError("Last name is required.")

        return last_name

    def clean_email(self):
        email = self.cleaned_data["email"].strip()

        if (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.user.pk)
            .exists()
        ):
            raise forms.ValidationError(
                "That email address is already in use."
            )

        return email

    @transaction.atomic
    def save(self, commit=True):
        customer = super().save(commit=False)

        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]

        if commit:
            self.user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )
            customer.save()

        return customer


class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        label="Verification code",
        min_length=6,
        max_length=6,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "placeholder": "Enter your 6-digit code",
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"]

        if not code.isascii() or not code.isdigit():
            raise forms.ValidationError(
                "Enter the six-digit verification code."
            )

        return code
