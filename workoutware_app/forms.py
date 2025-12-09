"""
Custom user registration form.

Extends Django's built-in UserCreationForm by adding:
- Email field (required)
- Email uniqueness validation
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """
    User registration form with:
        - username
        - email (required)
        - password1
        - password2

    Adds explicit validation to ensure each email address is unique.
    This mirrors Django's default username uniqueness behavior so
    template errors appear under form.email.errors.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        """
        Ensure the email address is unique across all users.

        Returns:
            str: The cleaned email.

        Raises:
            ValidationError: If the email is already in use.
        """
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")

        return email