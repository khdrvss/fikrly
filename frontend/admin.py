from django.contrib import admin
from django import forms
from urllib.parse import urlparse
import json
from django.conf import settings
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered
from .models import Company, Review, UserProfile, ActivityLog, ReviewReport, CompanyClaim
from pathlib import Path


class CompanyActivityLogInline(admin.TabularInline):
    model = ActivityLog
    fk_name = 'company'
    fields = ("created_at", "action", "actor", "details")
    readonly_fields = ("created_at", "action", "actor", "details")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ReviewActivityLogInline(admin.TabularInline):
    model = ActivityLog
    fk_name = 'review'
    fields = ("created_at", "action", "actor", "details")
    readonly_fields = ("created_at", "action", "actor", "details")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CompanyAdminForm(forms.ModelForm):
    library_image_path = forms.ChoiceField(label="Library image", required=False)
    working_hours = forms.CharField(
        label="Working hours (JSON)", required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'input-field font-mono',
            'placeholder': '{\n  "Mon": "09:00-18:00",\n  "Tue": "09:00-18:00"\n}'
        })
    )

    class Meta:
        model = Company
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_dir = getattr(settings, 'MEDIA_ROOT', '')
        folder = os.path.join(base_dir, 'company_library')
        choices = [('', '— No selection —')]
        exts = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for f in sorted(files):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in exts:
                        full = os.path.join(root, f)
                        rel = os.path.relpath(full, base_dir).replace('\\', '/')
                        choices.append((rel, rel))
        self.fields['library_image_path'].choices = choices
        # Pre-fill working_hours text if instance has JSON
        if self.instance and self.instance.pk and isinstance(self.instance.working_hours, (dict, list)):
            self.initial['working_hours'] = json.dumps(self.instance.working_hours, ensure_ascii=False, indent=2)

        # Make category a dropdown from categories_uz.json if available
        try:
            data_path = Path(__file__).resolve().parent / 'data' / 'categories_uz.json'
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Use human labels as both value and label for simplicity
            labels = sorted((v for v in data.values() if v), key=lambda s: s.lower())
            cat_choices = [('', '— Kategoriya tanlang —')] + [(lbl, lbl) for lbl in labels]
            self.fields['category'] = forms.ChoiceField(choices=cat_choices, required=False)
        except Exception:
            # Fallback keeps default text input
            pass

    def clean_working_hours(self):
        data = self.cleaned_data.get('working_hours')
        if not data:
            return None
        if isinstance(data, (dict, list)):
            return data
        try:
            parsed = json.loads(data)
            if isinstance(parsed, (dict, list)):
                return parsed
        except Exception:
            pass
        raise forms.ValidationError("JSON noto'g'ri formatda.")

    def clean(self):
        cleaned = super().clean()
        # Normalize website and infer domain if empty
        website = cleaned.get('website') or ''
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
            cleaned['website'] = website
        if website and not cleaned.get('official_email_domain'):
            try:
                netloc = urlparse(website).netloc.lower()
                if netloc.startswith('www.'):
                    netloc = netloc[4:]
                cleaned['official_email_domain'] = netloc
            except Exception:
                pass
        # Validate lat/lng ranges
        lat = cleaned.get('lat')
        lng = cleaned.get('lng')
        if lat is not None and (lat < -90 or lat > 90):
            self.add_error('lat', 'Latitude -90..90 oraliqda bo‘lishi kerak.')
        if lng is not None and (lng < -180 or lng > 180):
            self.add_error('lng', 'Longitude -180..180 oraliqda bo‘lishi kerak.')
        return cleaned


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = ("name", "category", "city", "manager", "rating", "review_count", "like_count", "is_verified")
    list_filter = ("category", "city", "is_verified")
    search_fields = ("name", "city", "category", "tax_id")
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Asosiy ma'lumot", {
            'fields': ("name", ("category", "city"), "description"),
        }),
        ("Media", {
            'fields': (("image_url", "image"), "library_image_path", "image_preview"),
        }),
        ("Aloqa", {
            'fields': (("website", "official_email_domain"), ("phone_public", "email_public")),
        }),
        ("Manzil", {
            'fields': (("tax_id", "address"), "landmark", ("lat", "lng")),
        }),
        ("Ish vaqti", {
            'fields': ("working_hours",),
        }),
        ("Ijtimoiy tarmoqlar", {
            'fields': (("facebook_url", "telegram_url", "instagram_url"),),
        }),
        ("Egalik va holat", {
            'fields': (("manager", "is_verified"), ("rating", "review_count", "like_count")),
        }),
    )
    inlines = [CompanyActivityLogInline]

    def image_preview(self, obj):
        from django.utils.html import format_html
        url = getattr(obj, 'display_image_url', '') or getattr(obj, 'image_url', '')
        if not url:
            return "—"
        return format_html('<img src="{}" style="max-height:80px;max-width:160px;border-radius:4px;"/>', url)
    image_preview.short_description = "Preview"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("company", "user_name", "rating", "is_approved", "verified_purchase", "created_at")
    list_filter = ("is_approved", "rating", "verified_purchase", "company")
    search_fields = ("company__name", "user_name", "text")
    actions = ["approve_reviews"]
    inlines = [ReviewActivityLogInline]

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} ta sharh tasdiqlandi.")
    approve_reviews.short_description = "Tanlangan sharhlarni tasdiqlash"

# Ensure the built-in User model is visible/customized in the admin pane
User = get_user_model()
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email")

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_approved", "requested_approval_at", "approved_at")
    list_filter = ("is_approved",)
    search_fields = ("user__username", "user__email")
    actions = [
        'approve_profiles',
    ]

    def approve_profiles(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_approved=True, approved_at=timezone.now())
        self.message_user(request, f"{updated} profil tasdiqlandi.")
    approve_profiles.short_description = "Tanlangan profillarni tasdiqlash"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("created_at", "action", "actor", "company", "review", "short_details")
    list_filter = ("action", "actor", "company", "review")
    search_fields = ("details", "company__name", "review__text", "actor__username")
    actions = ["export_csv"]

    def short_details(self, obj):
        txt = obj.details or ""
        return (txt[:80] + "…") if len(txt) > 80 else txt
    short_details.short_description = "Details"

    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=activity_logs.csv'
        writer = csv.writer(response)
        writer.writerow(["created_at", "action", "actor", "company", "review", "details"])
        for obj in queryset.select_related('actor', 'company', 'review'):
            writer.writerow([
                obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                obj.get_action_display() if hasattr(obj, 'get_action_display') else obj.action,
                getattr(obj.actor, 'username', ''),
                getattr(obj.company, 'name', '') if obj.company_id else '',
                f"#{obj.review_id}" if obj.review_id else '',
                (obj.details or '').replace('\n', ' ').replace('\r', ' '),
            ])
        return response
    export_csv.short_description = "Export selected logs to CSV"


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "reason", "status", "created_at", "reporter")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("details", "review__text", "review__company__name", "reporter__username")
    actions = ["mark_resolved", "mark_rejected"]

    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} ta xabar 'Hal qilindi' deb belgilandi.")

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} ta xabar 'Rad etildi' deb belgilandi.")


@admin.register(CompanyClaim)
class CompanyClaimAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ("company", "email", "status", "created_at", "verified_at", "claimant")
    list_filter = ("status", "created_at")
    search_fields = ("company__name", "email", "claimant__username")
    readonly_fields = ("company", "claimant", "email", "token", "status", "created_at", "verified_at", "expires_at", "request_ip", "user_agent")


from .models import Category

class CategoryAdminForm(forms.ModelForm):
    """Custom form for Category admin with better icon field"""
    icon_svg = forms.CharField(
        label="SVG Icon",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'font-mono',
            'placeholder': '<path d="M12 2L2 7L12 12L22 7L12 2Z"/>'
        }),
        help_text="SVG path elementi. Masalan: &lt;path d='M12 2L2 7L12 12L22 7L12 2Z'/&gt;"
    )
    
    class Meta:
        model = Category
        fields = '__all__'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ('name', 'slug', 'color', 'is_active', 'sort_order', 'company_count', 'review_count', 'created_at')
    list_filter = ('color', 'is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'sort_order', 'color')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Dizayn', {
            'fields': ('icon_svg', 'color', 'sort_order'),
            'description': 'Kategoriya ko\'rinishi uchun sozlamalar'
        }),
        ('Statistika', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def company_count(self, obj):
        """Display company count for this category"""
        return obj.company_count
    company_count.short_description = 'Kompaniyalar soni'
    
    def review_count(self, obj):
        """Display review count for this category"""
        return obj.review_count
    review_count.short_description = 'Sharhlar soni'
