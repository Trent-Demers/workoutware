"""
Custom user registration form.

Extends Django's built-in UserCreationForm by adding:
- Email field (required)
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """
    User registration form with email support.

    Django's built-in UserCreationForm provides:
        - username
        - password1
        - password2

    This subclass adds:
        - email (required)
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
