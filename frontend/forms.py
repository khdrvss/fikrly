from django import forms
from .models import UserProfile, Review, Company, ReviewReport, BusinessCategory
from django.utils.translation import gettext_lazy as _


class ReviewForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        empty_label=_("Kompaniya tanlang"),
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    class Meta:
        model = Review
        fields = ["company", "user_name", "rating", "text", "receipt"]
        widgets = {
            "user_name": forms.TextInput(attrs={"class": "input-field"}),
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "input-field"}
            ),
            "text": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
            "receipt": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                }
            ),
        }
        labels = {
            "receipt": _("Xarid cheki (ixtiyoriy)"),
        }

    def clean_receipt(self):
        receipt = self.cleaned_data.get("receipt")
        if receipt:
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Fayl hajmi 5MB dan oshmasligi kerak."))
        return receipt


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("Ism"),
        widget=forms.TextInput(attrs={"class": "input-field"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label=_("Familiya"),
        widget=forms.TextInput(attrs={"class": "input-field"}),
    )

    class Meta:
        model = UserProfile
        fields = ["avatar", "bio"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.instance.user:
            self.instance.user.first_name = self.cleaned_data["first_name"]
            self.instance.user.last_name = self.cleaned_data["last_name"]
            if commit:
                self.instance.user.save()
                profile.save()
        return profile


class ReviewEditForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text", "receipt"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={"min": 1, "max": 5, "class": "input-field"}
            ),
            "text": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
            "receipt": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                }
            ),
        }
        labels = {
            "receipt": _("Xarid cheki (ixtiyoriy)"),
        }

    def clean_receipt(self):
        receipt = self.cleaned_data.get("receipt")
        if receipt:
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Fayl hajmi 5MB dan oshmasligi kerak."))
        return receipt


class ReportReviewForm(forms.ModelForm):
    # Honeypot: real users won't see/fill this
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "tabindex": "-1",
                "aria-hidden": "true",
                "class": "hidden",
            }
        ),
    )

    class Meta:
        model = ReviewReport
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.Select(attrs={"class": "input-field"}),
            "details": forms.Textarea(attrs={"rows": 4, "class": "input-field"}),
        }
        labels = {
            "reason": _("Sabab"),
            "details": _("Qo‘shimcha maʼlumot (ixtiyoriy)"),
        }

    def clean(self):
        cleaned = super().clean()
        # Honeypot must be empty
        if cleaned.get("website"):
            raise forms.ValidationError(_("Form xatosi. Iltimos qayta urinib ko‘ring."))
        return cleaned


class CompanyManagerEditForm(forms.ModelForm):
    category_fk = forms.ModelChoiceField(
        queryset=BusinessCategory.objects.all(),
        label=_("Kategoriya"),
        widget=forms.Select(attrs={"class": "input-field"}),
        required=False,
    )

    class Meta:
        model = Company
        fields = [
            "name",
            "category_fk",
            "city",
            "description",
            "description_ru",
            "image",
            "library_image_path",
            "image_url",
            "logo",
            "logo_url",
            "logo_scale",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input-field"}),
            "city": forms.TextInput(attrs={"class": "input-field"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
            "description_ru": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
            "image": forms.FileInput(
                attrs={
                    "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                }
            ),
            "library_image_path": forms.TextInput(attrs={"class": "input-field"}),
            "image_url": forms.URLInput(attrs={"class": "input-field"}),
            "logo_scale": forms.NumberInput(
                attrs={"class": "input-field", "min": "50", "max": "200", "step": "5"}
            ),
        }


class ReviewApprovalRequestForm(forms.Form):
    confirm = forms.BooleanField(
        label=_("Tasdiqlashni so'rashni tasdiqlayman"), required=True
    )


class OwnerResponseForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["owner_response_text"]
        widgets = {
            "owner_response_text": forms.Textarea(
                attrs={"rows": 4, "class": "input-field h-32 resize-none"}
            ),
        }
        labels = {
            "owner_response_text": _("Biznes javobi"),
        }


class ClaimCompanyForm(forms.Form):
    email = forms.EmailField(
        label="Ishchi email", widget=forms.EmailInput(attrs={"class": "input-field"})
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        return email


class ContactForm(forms.Form):
    name = forms.CharField(
        label=_("Ismingiz"),
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input-field"}),
    )
    email = forms.EmailField(
        label=_("Email manzilingiz"),
        widget=forms.EmailInput(attrs={"class": "input-field"}),
    )
    subject = forms.CharField(
        label=_("Mavzu"),
        max_length=200,
        widget=forms.TextInput(attrs={"class": "input-field"}),
    )
    message = forms.CharField(
        label=_("Xabar"),
        widget=forms.Textarea(
            attrs={"rows": 5, "class": "input-field h-32 resize-none"}
        ),
    )
