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
        choices=Customer.ContactPreference.choices
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
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.email = self.cleaned_data["email"].strip()

        if commit:
            user.save()
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

        self.user.first_name = self.cleaned_data["first_name"].strip()
        self.user.last_name = self.cleaned_data["last_name"].strip()
        self.user.email = self.cleaned_data["email"].strip()

        if commit:
            self.user.save(
                update_fields=["first_name", "last_name", "email"]
            )
            customer.save()

        return customer
