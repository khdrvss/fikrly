from django import forms
from urllib.parse import urlparse
from .models import UserProfile, Review, Company, ReviewReport
from django import forms



class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'input-field h-32 resize-none'}),
        }


class ReviewEditForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'input-field'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'input-field h-32 resize-none'}),
        }


class ReportReviewForm(forms.ModelForm):
    # Honeypot: real users won't see/fill this
    website = forms.CharField(required=False, label="", widget=forms.TextInput(attrs={
        'autocomplete': 'off',
        'tabindex': '-1',
        'aria-hidden': 'true',
        'class': 'hidden',
    }))
    class Meta:
        model = ReviewReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'input-field'}),
            'details': forms.Textarea(attrs={'rows': 4, 'class': 'input-field'}),
        }
        labels = {
            'reason': 'Sabab',
            'details': 'Qo‘shimcha maʼlumot (ixtiyoriy)',
        }

    def clean(self):
        cleaned = super().clean()
        # Honeypot must be empty
        if cleaned.get('website'):
            raise forms.ValidationError('Form xatosi. Iltimos qayta urinib ko‘ring.')
        return cleaned


class CompanyManagerEditForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'category', 'city', 'description', 'image', 'library_image_path', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input-field'}),
            'category': forms.TextInput(attrs={'class': 'input-field'}),
            'city': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'input-field h-32 resize-none'}),
            'image_url': forms.URLInput(attrs={'class': 'input-field'}),
        }


class ReviewApprovalRequestForm(forms.Form):
    confirm = forms.BooleanField(label="Tasdiqlashni so'rashni tasdiqlayman", required=True)


class OwnerResponseForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['owner_response_text']
        widgets = {
            'owner_response_text': forms.Textarea(attrs={'rows': 4, 'class': 'input-field h-32 resize-none'}),
        }
        labels = {
            'owner_response_text': "Biznes javobi",
        }


class ClaimCompanyForm(forms.Form):
    email = forms.EmailField(label="Ishchi email", widget=forms.EmailInput(attrs={'class': 'input-field'}))

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        domain = email.split('@')[-1]
        # If company has an official domain, require match; otherwise try website domain
        if self.company:
            expected = (self.company.official_email_domain or '').lower().strip()
            if expected:
                if domain != expected:
                    raise forms.ValidationError(f"Email domeni {expected} bo‘lishi kerak.")
            elif self.company.website:
                try:
                    netloc = urlparse(self.company.website).netloc.lower()
                    if netloc.startswith('www.'):
                        netloc = netloc[4:]
                    # accept exact domain or subdomain of website domain
                    if not (domain == netloc or domain.endswith('.' + netloc)):
                        raise forms.ValidationError(f"Email domeni {netloc} bilan mos bo‘lishi kerak.")
                except Exception:
                    pass
        return email
