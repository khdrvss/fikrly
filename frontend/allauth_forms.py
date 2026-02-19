from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _


class CustomSignupForm(SignupForm):
    """Custom signup form that enforces Gmail domain restriction"""

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and not email.endswith("@gmail.com"):
            raise forms.ValidationError(_("Faqat Gmail domeniga ruxsat berilgan"))
        return email
