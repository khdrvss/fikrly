from django import forms
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import UserProfile, Review, Company, ReviewReport, BusinessCategory, BusinessOwnershipClaim
from django.utils.translation import gettext_lazy as _
from .visibility import public_companies_queryset


class ReviewForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        empty_label=_("Kompaniya tanlang"),
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].queryset = public_companies_queryset()

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
    USERNAME_CHANGE_LIMIT = 2
    USERNAME_CHANGE_WINDOW_DAYS = 3

    username = forms.CharField(
        max_length=150,
        required=False,
        label=_("Username"),
        widget=forms.TextInput(attrs={"class": "input-field"}),
    )

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
            self.fields["username"].initial = self.instance.user.username
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not self.instance or not self.instance.user:
            if not username:
                raise forms.ValidationError(_("Username kiritilishi shart."))
            return username

        if not username:
            return (self.instance.user.username or "").strip()

        current_username = (self.instance.user.username or "").strip()
        if username == current_username:
            return username

        User = get_user_model()
        username_exists = User.objects.filter(username__iexact=username).exclude(
            pk=self.instance.user_id
        ).exists()
        if username_exists:
            raise forms.ValidationError(_("Bu username allaqachon band."))

        now = timezone.now()
        window_start = now - timedelta(days=self.USERNAME_CHANGE_WINDOW_DAYS)
        history = self.instance.username_change_log or []
        valid_history = []
        for item in history:
            try:
                changed_at = timezone.datetime.fromisoformat(str(item))
                if timezone.is_naive(changed_at):
                    changed_at = timezone.make_aware(
                        changed_at, timezone.get_current_timezone()
                    )
                if changed_at >= window_start:
                    valid_history.append(changed_at)
            except Exception:
                continue

        if len(valid_history) >= self.USERNAME_CHANGE_LIMIT:
            raise forms.ValidationError(
                _(
                    "Username ni 3 kun ichida faqat 2 marta o'zgartirish mumkin. Keyinroq urinib ko'ring."
                )
            )

        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.instance.user:
            old_username = (self.instance.user.username or "").strip()
            new_username = (self.cleaned_data.get("username") or "").strip()

            profile_history = profile.username_change_log or []
            now = timezone.now()
            window_start = now - timedelta(days=self.USERNAME_CHANGE_WINDOW_DAYS)
            pruned_history = []
            for item in profile_history:
                try:
                    changed_at = timezone.datetime.fromisoformat(str(item))
                    if timezone.is_naive(changed_at):
                        changed_at = timezone.make_aware(
                            changed_at, timezone.get_current_timezone()
                        )
                    if changed_at >= window_start:
                        pruned_history.append(changed_at.isoformat())
                except Exception:
                    continue

            if new_username and new_username != old_username:
                self.instance.user.username = new_username
                pruned_history.append(now.isoformat())

            profile.username_change_log = pruned_history
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


class BusinessOwnershipClaimForm(forms.Form):
    POSITION_CHOICES = BusinessOwnershipClaim.POSITION_CHOICES

    full_name = forms.CharField(
        label=_("To'liq ism"),
        max_length=200,
        widget=forms.TextInput(attrs={"class": "input-field", "placeholder": _("Ali Karimov")}),
    )
    phone = forms.CharField(
        label=_("Telefon raqam"),
        max_length=30,
        widget=forms.TextInput(attrs={"class": "input-field", "placeholder": "+998901234567"}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "input-field", "placeholder": "ali@example.com"}),
    )
    position = forms.ChoiceField(
        label=_("Kompaniyadagi lavozim"),
        choices=POSITION_CHOICES,
        widget=forms.Select(attrs={"class": "input-field"}),
    )
    proof_file = forms.FileField(
        label=_("Tasdiq hujjati (PDF yoki rasm)"),
        required=False,
        widget=forms.FileInput(attrs={"class": "input-field", "accept": "image/*,application/pdf"}),
    )
    comment = forms.CharField(
        label=_("Izoh (ixtiyoriy)"),
        required=False,
        widget=forms.Textarea(attrs={"class": "input-field h-20 resize-none", "rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        import re
        phone = self.cleaned_data["phone"].strip()
        if not re.match(r"^\+?[\d\s\-\(\)]{7,20}$", phone):
            raise forms.ValidationError(_("Noto'g'ri telefon raqam formati."))
        return phone

    def clean_proof_file(self):
        f = self.cleaned_data.get("proof_file")
        if f:
            allowed = ["application/pdf", "image/jpeg", "image/png", "image/webp", "image/jpg"]
            content_type = getattr(f, "content_type", "")
            if content_type not in allowed:
                raise forms.ValidationError(_("Faqat PDF yoki rasm fayllari qabul qilinadi."))
            if f.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Fayl hajmi 5MB dan oshmasligi kerak."))
        return f


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
