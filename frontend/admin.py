from django.contrib import admin
from django import forms
from urllib.parse import urlparse
import json
from django.conf import settings
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered
from .models import (
    Company,
    Review,
    UserProfile,
    ActivityLog,
    ReviewReport,
    CompanyClaim,
    BusinessCategory,
    ReviewHelpfulVote,
    UserGamification,
    Badge,
    TwoFactorAuth,
    ReviewImage,
    ReviewFlag,
    DataExport,
)
from .cache_utils import clear_public_cache
from pathlib import Path


@admin.action(description="Clear public cache (emergency refresh)")
def clear_public_cache_action(modeladmin, request, queryset):
    deleted = clear_public_cache()
    if deleted == -1:
        modeladmin.message_user(
            request,
            "Public cache tozalandi (backend fallback orqali).",
            level="warning",
        )
    else:
        modeladmin.message_user(
            request,
            f"Public cache tozalandi. O'chirilgan keylar: {deleted}",
        )


class CompanyActivityLogInline(admin.TabularInline):
    model = ActivityLog
    fk_name = "company"
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
    fk_name = "review"
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
        label="Working hours (JSON)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "class": "input-field font-mono",
                "placeholder": '{\n  "Mon": "09:00-18:00",\n  "Tue": "09:00-18:00"\n}',
            }
        ),
    )

    class Meta:
        model = Company
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_dir = getattr(settings, "MEDIA_ROOT", "")
        folder = os.path.join(base_dir, "company_library")
        choices = [("", "— No selection —")]
        exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for f in sorted(files):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in exts:
                        full = os.path.join(root, f)
                        rel = os.path.relpath(full, base_dir).replace("\\", "/")
                        choices.append((rel, rel))
        self.fields["library_image_path"].choices = choices
        # Pre-fill working_hours text if instance has JSON
        if (
            self.instance
            and self.instance.pk
            and isinstance(self.instance.working_hours, (dict, list))
        ):
            self.initial["working_hours"] = json.dumps(
                self.instance.working_hours, ensure_ascii=False, indent=2
            )

        # Make category a dropdown from categories_uz.json if available
        try:
            data_path = Path(__file__).resolve().parent / "data" / "categories_uz.json"
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Use human labels as both value and label for simplicity
            labels = sorted((v for v in data.values() if v), key=lambda s: s.lower())
            cat_choices = [("", "— Kategoriya tanlang —")] + [
                (lbl, lbl) for lbl in labels
            ]
            self.fields["category"] = forms.ChoiceField(
                choices=cat_choices, required=False
            )
        except Exception:
            # Fallback keeps default text input
            pass

    def clean_working_hours(self):
        data = self.cleaned_data.get("working_hours")
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
        website = cleaned.get("website") or ""
        if website and not website.startswith(("http://", "https://")):
            website = "https://" + website
            cleaned["website"] = website
        if website and not cleaned.get("official_email_domain"):
            try:
                netloc = urlparse(website).netloc.lower()
                if netloc.startswith("www."):
                    netloc = netloc[4:]
                cleaned["official_email_domain"] = netloc
            except Exception:
                pass
        # Validate lat/lng ranges
        lat = cleaned.get("lat")
        lng = cleaned.get("lng")
        if lat is not None and (lat < -90 or lat > 90):
            self.add_error("lat", "Latitude -90..90 oraliqda bo‘lishi kerak.")
        if lng is not None and (lng < -180 or lng > 180):
            self.add_error("lng", "Longitude -180..180 oraliqda bo‘lishi kerak.")
        return cleaned


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ru", "slug")
    search_fields = ("name", "name_ru")
    prepopulated_fields = {"slug": ("name",)}
    actions = [clear_public_cache_action]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm
    list_display = (
        "name",
        "category_fk",
        "city",
        "manager",
        "rating",
        "review_count",
        "like_count",
        "is_verified",
        "is_active",
    )
    list_filter = ("category_fk", "city", "is_verified", "is_active")
    search_fields = ("name", "city", "category_fk__name", "tax_id")
    readonly_fields = ("image_preview",)
    actions = [
        "approve_verification",
        "reject_verification",
        "toggle_verified",
        "email_managers",
        "export_to_csv",
    ]
    fieldsets = (
        (
            "Asosiy ma'lumot",
            {
                "fields": (
                    "name",
                    ("category_fk", "city"),
                    "description",
                    "description_ru",
                ),
            },
        ),
        (
            "Media",
            {
                "fields": (
                    ("image_url", "image"),
                    ("logo_url", "logo"),
                    "logo_scale",
                    "library_image_path",
                    "image_preview",
                ),
            },
        ),
        (
            "Aloqa",
            {
                "fields": (
                    ("website", "official_email_domain"),
                    ("phone_public", "email_public"),
                ),
            },
        ),
        (
            "Manzil",
            {
                "fields": (("tax_id", "address"), "landmark", ("lat", "lng")),
            },
        ),
        (
            "Ish vaqti",
            {
                "fields": ("working_hours",),
            },
        ),
        (
            "Ijtimoiy tarmoqlar",
            {
                "fields": (("facebook_url", "telegram_url", "instagram_url"),),
            },
        ),
        (
            "Egalik va holat",
            {
                "fields": (
                    ("manager", "is_verified", "is_active"),
                    ("verification_requested_at", "verification_document"),
                    "verification_notes",
                    ("rating", "review_count", "like_count"),
                ),
            },
        ),
    )
    inlines = [CompanyActivityLogInline]
    actions = [
        "toggle_visibility",
        "toggle_verified",
        "approve_verification",
        "reject_verification",
        clear_public_cache_action,
    ]

    def toggle_visibility(self, request, queryset):
        for company in queryset:
            company.is_active = not company.is_active
            company.save(update_fields=["is_active"])
        self.message_user(
            request, f"{queryset.count()} ta kompaniya holati o'zgartirildi."
        )

    toggle_visibility.short_description = (
        "Ko'rinish holatini o'zgartirish (Active/Inactive)"
    )

    def approve_verification(self, request, queryset):
        """Bulk approve business verification"""
        from django.utils import timezone

        count = 0
        for company in queryset.filter(is_verified=False):
            if company.verification_document:
                company.is_verified = True
                company.verification_notes = (
                    f'Tasdiqlangan - {timezone.now().strftime("%Y-%m-%d %H:%M")}'
                )
                company.save()
                count += 1
        self.message_user(request, f"{count} ta biznes tasdiqlandi")

    approve_verification.short_description = "Biznes tasdiqlamasini tasdiqlash"

    def reject_verification(self, request, queryset):
        """Bulk reject business verification"""
        from django.utils import timezone

        count = 0
        for company in queryset.filter(is_verified=False):
            if company.verification_requested_at:
                company.verification_document = None
                company.verification_requested_at = None
                company.verification_notes = (
                    f'Rad etilgan - {timezone.now().strftime("%Y-%m-%d %H:%M")}'
                )
                company.save()
                count += 1
        self.message_user(request, f"{count} ta so'rov rad etildi")

    reject_verification.short_description = "Biznes tasdiqlamasini rad etish"

    def toggle_verified(self, request, queryset):
        for company in queryset:
            company.is_verified = not company.is_verified
            company.save(update_fields=["is_verified"])
        self.message_user(
            request, f"{queryset.count()} ta kompaniya tasdiqlash holati o'zgartirildi."
        )

    toggle_verified.short_description = (
        "Tasdiqlash holatini o'zgartirish (Verified/Not Verified)"
    )

    def email_managers(self, request, queryset):
        """Bulk action to email all managers of selected companies"""
        from django.core.mail import send_mail
        from django.conf import settings

        managers = (
            queryset.exclude(manager__isnull=True)
            .values_list("manager__email", flat=True)
            .distinct()
        )
        managers = [email for email in managers if email]

        if not managers:
            self.message_user(
                request,
                "Tanlangan bizneslarda email manzili bo'lgan menejerlar yo'q",
                level="warning",
            )
            return

        try:
            send_mail(
                subject="Fikrly - Muhim xabar",
                message="Hurmatli biznes menedjer,\n\nBu Fikrly platformasi tomonidan yuborilgan xabar.\n\nHurmat bilan,\nFikrly jamoasi",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=managers,
                fail_silently=False,
            )
            self.message_user(request, f"{len(managers)} ta menejerga email yuborildi")
        except Exception as e:
            self.message_user(request, f"Email yuborishda xatolik: {e}", level="error")

    email_managers.short_description = (
        "Tanlangan bizneslar menejerlariga email yuborish"
    )

    def export_to_csv(self, request, queryset):
        """Bulk action to export companies to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="companies.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Name",
                "Category",
                "City",
                "Rating",
                "Reviews",
                "Verified",
                "Active",
            ]
        )

        for company in queryset:
            writer.writerow(
                [
                    company.id,
                    company.name,
                    company.category_fk.name if company.category_fk else "",
                    company.city,
                    company.rating or 0,
                    company.review_count or 0,
                    "Ha" if company.is_verified else "Yo'q",
                    "Faol" if company.is_active else "Nofaol",
                ]
            )

        return response

    export_to_csv.short_description = "Tanlangan bizneslarni CSV ga export qilish"

    def image_preview(self, obj):
        from django.utils.html import format_html

        logo_src = None
        if obj.logo:
            try:
                if obj.logo.name and obj.logo.storage.exists(obj.logo.name):
                    logo_src = obj.logo.url
            except Exception:
                logo_src = None
        if not logo_src and getattr(obj, "logo_url", None):
            logo_src = obj.logo_url
        elif not logo_src and getattr(obj, "logo_url_backup", None):
            logo_src = obj.logo_url_backup

        if logo_src:
            return format_html(
                '<div style="display:flex;gap:10px;">'
                '<div><small>Logo:</small><br><img src="{}" style="max-height:80px;max-width:80px;border-radius:4px;object-fit:cover;"/></div>'
                "</div>",
                logo_src,
            )

        url = getattr(obj, "display_image_url", "") or getattr(obj, "image_url", "")
        if not url:
            return "—"
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:160px;border-radius:4px;"/>',
            url,
        )

    image_preview.short_description = "Preview"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "user_name",
        "rating",
        "is_approved",
        "verified_purchase",
        "created_at",
        "has_receipt",
    )
    list_filter = ("is_approved", "rating", "verified_purchase", "company")
    search_fields = ("company__name", "user_name", "text")
    actions = [
        "approve_reviews",
        "toggle_verified_purchase",
        "bulk_reject_reviews",
        "export_reviews_csv",
        clear_public_cache_action,
    ]
    inlines = [ReviewActivityLogInline]
    readonly_fields = ("receipt_preview",)

    def has_receipt(self, obj):
        return bool(obj.receipt)

    has_receipt.boolean = True
    has_receipt.short_description = "Chek bormi?"

    def receipt_preview(self, obj):
        if obj.receipt:
            from django.utils.safestring import mark_safe

            return mark_safe(
                f'<a href="{obj.receipt.url}" target="_blank"><img src="{obj.receipt.url}" style="max-height: 300px; max-width: 100%;" /></a>'
            )
        return "Chek yuklanmagan"

    receipt_preview.short_description = "Chek ko'rinishi"

    def toggle_verified_purchase(self, request, queryset):
        for review in queryset:
            review.verified_purchase = not review.verified_purchase
            review.save(update_fields=["verified_purchase"])
        self.message_user(
            request, f"{queryset.count()} ta sharh xarid tasdiqlanishi o'zgartirildi."
        )

    toggle_verified_purchase.short_description = "Xaridni tasdiqlash/bekor qilish"

    def approve_reviews(self, request, queryset):
        # Get affected company IDs before update
        company_ids = list(queryset.values_list("company_id", flat=True).distinct())
        updated = queryset.update(is_approved=True)

        # Recalculate stats for affected companies
        from .utils import recalculate_company_stats

        for cid in company_ids:
            recalculate_company_stats(cid)

        self.message_user(request, f"{updated} ta sharh tasdiqlandi.")

    approve_reviews.short_description = "Tanlangan sharhlarni tasdiqlash"

    def bulk_reject_reviews(self, request, queryset):
        """Bulk reject/unapprove reviews"""
        company_ids = list(queryset.values_list("company_id", flat=True).distinct())
        updated = queryset.update(is_approved=False)

        # Recalculate stats
        from .models import Company
        from django.db.models import Avg, Count

        for company_id in company_ids:
            company = Company.objects.get(pk=company_id)
            approved_reviews = Review.objects.filter(company=company, is_approved=True)
            company.rating = approved_reviews.aggregate(Avg("rating"))["rating__avg"]
            company.review_count = approved_reviews.count()
            company.save(update_fields=["rating", "review_count"])

        self.message_user(request, f"{updated} sharh rad etildi (is_approved=False).")

    bulk_reject_reviews.short_description = "Tanlangan sharhlarni rad etish"

    def export_reviews_csv(self, request, queryset):
        """Export reviews to CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="reviews.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Company",
                "User",
                "Rating",
                "Text",
                "Approved",
                "Verified Purchase",
                "Created",
            ]
        )

        for review in queryset:
            writer.writerow(
                [
                    review.id,
                    review.company.name,
                    review.user_name
                    or (review.author.username if review.author else ""),
                    review.rating,
                    review.text[:100],  # Truncate long text
                    "Ha" if review.is_approved else "Yo'q",
                    "Ha" if review.verified_purchase else "Yo'q",
                    review.created_at.strftime("%Y-%m-%d %H:%M"),
                ]
            )

        return response

    export_reviews_csv.short_description = "Tanlangan sharhlarni CSV ga export qilish"


# Ensure the built-in User model is visible/customized in the admin pane
User = get_user_model()
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "get_is_approved",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "profile__is_approved")
    search_fields = ("username", "email")
    actions = ["approve_users"]

    def get_is_approved(self, obj):
        return obj.profile.is_approved if hasattr(obj, "profile") else False

    get_is_approved.boolean = True
    get_is_approved.short_description = "Approved"

    def approve_users(self, request, queryset):
        from django.utils import timezone

        count = 0
        for user in queryset:
            if hasattr(user, "profile"):
                user.profile.is_approved = True
                user.profile.approved_at = timezone.now()
                user.profile.save()
                count += 1
        self.message_user(request, f"{count} ta foydalanuvchi tasdiqlandi.")

    approve_users.short_description = "Tanlangan foydalanuvchilarni tasdiqlash"


# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "get_email",
        "is_approved",
        "requested_approval_at",
        "approved_at",
    )
    list_filter = ("is_approved",)
    search_fields = ("user__username", "user__email")
    actions = [
        "approve_profiles",
    ]

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"
    get_email.admin_order_field = "user__email"

    def approve_profiles(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(is_approved=True, approved_at=timezone.now())
        self.message_user(request, f"{updated} profil tasdiqlandi.")

    approve_profiles.short_description = "Tanlangan profillarni tasdiqlash"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "created_at",
        "action",
        "actor",
        "company",
        "review",
        "short_details",
    )
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

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=activity_logs.csv"
        writer = csv.writer(response)
        writer.writerow(
            ["created_at", "action", "actor", "company", "review", "details"]
        )
        for obj in queryset.select_related("actor", "company", "review"):
            writer.writerow(
                [
                    obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        obj.get_action_display()
                        if hasattr(obj, "get_action_display")
                        else obj.action
                    ),
                    getattr(obj.actor, "username", ""),
                    getattr(obj.company, "name", "") if obj.company_id else "",
                    f"#{obj.review_id}" if obj.review_id else "",
                    (obj.details or "").replace("\n", " ").replace("\r", " "),
                ]
            )
        return response

    export_csv.short_description = "Export selected logs to CSV"


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "reason", "status", "created_at", "reporter")
    list_filter = ("status", "reason", "created_at")
    search_fields = (
        "details",
        "review__text",
        "review__company__name",
        "reporter__username",
    )
    actions = ["mark_resolved", "mark_rejected"]

    def mark_resolved(self, request, queryset):
        updated = queryset.update(status="resolved")
        self.message_user(request, f"{updated} ta xabar 'Hal qilindi' deb belgilandi.")

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} ta xabar 'Rad etildi' deb belgilandi.")


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "user", "vote_type", "created_at")
    list_filter = ("vote_type", "created_at")
    search_fields = ("review__text", "review__company__name", "user__username")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(CompanyClaim)
class CompanyClaimAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = (
        "company",
        "email",
        "status",
        "created_at",
        "verified_at",
        "claimant",
    )
    list_filter = ("status", "created_at")
    search_fields = ("company__name", "email", "claimant__username")
    readonly_fields = (
        "company",
        "claimant",
        "email",
        "token",
        "status",
        "created_at",
        "verified_at",
        "expires_at",
        "request_ip",
        "user_agent",
    )


from .models import Category


class CategoryAdminForm(forms.ModelForm):
    """Custom form for Category admin with better icon field"""

    icon_svg = forms.CharField(
        label="SVG Icon",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "font-mono",
                "placeholder": '<path d="M12 2L2 7L12 12L22 7L12 2Z"/>',
            }
        ),
        help_text="SVG path elementi. Masalan: &lt;path d='M12 2L2 7L12 12L22 7L12 2Z'/&gt;",
    )

    class Meta:
        model = Category
        fields = "__all__"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = (
        "id",
        "name",
        "slug",
        "color",
        "is_active",
        "sort_order",
        "company_count",
        "review_count",
        "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("color", "is_active", "created_at")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("name", "is_active", "sort_order", "color")
    ordering = ("sort_order", "name")

    fieldsets = (
        (
            "Asosiy ma'lumotlar",
            {"fields": ("name", "slug", "description", "is_active")},
        ),
        (
            "Dizayn",
            {
                "fields": ("icon_svg", "color", "sort_order"),
                "description": "Kategoriya ko'rinishi uchun sozlamalar",
            },
        ),
        (
            "Statistika",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def company_count(self, obj):
        """Display company count for this category"""
        return obj.company_count

    company_count.short_description = "Kompaniyalar soni"

    def review_count(self, obj):
        """Display review count for this category"""
        return obj.review_count

    review_count.short_description = "Sharhlar soni"


@admin.register(UserGamification)
class UserGamificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "level",
        "xp",
        "total_reviews",
        "helpful_votes_received",
        "current_streak",
    )
    list_filter = ("level", "current_streak")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "next_level_xp", "xp_progress")

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Progress", {"fields": ("level", "xp", "next_level_xp", "xp_progress")}),
        (
            "Statistics",
            {
                "fields": (
                    "total_reviews",
                    "helpful_votes_received",
                    "companies_reviewed",
                )
            },
        ),
        (
            "Streak",
            {"fields": ("current_streak", "longest_streak", "last_activity_date")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "badge_type", "icon", "earned_at", "is_new")
    list_filter = ("badge_type", "is_new", "earned_at")
    search_fields = ("user__username", "name", "description")
    readonly_fields = ("earned_at",)

    fieldsets = (
        (
            "Badge Info",
            {"fields": ("user", "badge_type", "name", "description", "icon")},
        ),
        ("Status", {"fields": ("is_new", "earned_at")}),
    )


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ("user", "is_enabled", "last_used", "created_at")
    list_filter = ("is_enabled", "last_used")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "secret_key")

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Settings", {"fields": ("is_enabled", "secret_key")}),
        ("Backup Codes", {"fields": ("backup_codes",)}),
        ("Activity", {"fields": ("last_used", "created_at")}),
    )


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ("review", "caption", "order", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("review__text", "caption")
    readonly_fields = ("uploaded_at",)

    fieldsets = (
        ("Review", {"fields": ("review",)}),
        ("Image", {"fields": ("image", "caption", "order")}),
        ("Timestamp", {"fields": ("uploaded_at",)}),
    )


@admin.register(ReviewFlag)
class ReviewFlagAdmin(admin.ModelAdmin):
    list_display = ("review", "flagged_by", "reason", "is_resolved", "created_at")
    list_filter = ("is_resolved", "reason", "created_at")
    search_fields = ("review__text", "flagged_by__username", "description")
    readonly_fields = ("created_at", "resolved_at")
    actions = ["resolve_as_approved", "resolve_as_deleted", "resolve_as_ignored"]

    fieldsets = (
        ("Flag Info", {"fields": ("review", "flagged_by", "reason", "description")}),
        (
            "Resolution",
            {"fields": ("is_resolved", "resolved_by", "resolved_at", "action_taken")},
        ),
        ("Timestamp", {"fields": ("created_at",)}),
    )

    def resolve_as_approved(self, request, queryset):
        """Bulk action: Approve flagged reviews"""
        from django.utils import timezone

        count = 0
        for flag in queryset.filter(is_resolved=False):
            flag.review.is_approved = True
            flag.review.save()
            flag.is_resolved = True
            flag.resolved_by = request.user
            flag.resolved_at = timezone.now()
            flag.action_taken = "Review approved by admin"
            flag.save()
            count += 1
        self.message_user(request, f"{count} ta sharh tasdiqlandi")

    resolve_as_approved.short_description = "Tanlangan sharhlarni tasdiqlash"

    def resolve_as_deleted(self, request, queryset):
        """Bulk action: Delete flagged reviews"""
        from django.utils import timezone

        count = 0
        for flag in queryset.filter(is_resolved=False):
            flag.review.delete()
            flag.is_resolved = True
            flag.resolved_by = request.user
            flag.resolved_at = timezone.now()
            flag.action_taken = "Review deleted by admin"
            flag.save()
            count += 1
        self.message_user(request, f"{count} ta sharh o'chirildi")

    resolve_as_deleted.short_description = "Tanlangan sharhlarni o'chirish"

    def resolve_as_ignored(self, request, queryset):
        """Bulk action: Ignore flags"""
        from django.utils import timezone

        count = queryset.filter(is_resolved=False).update(
            is_resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now(),
            action_taken="Flag ignored by admin",
        )
        self.message_user(request, f"{count} ta flag e'tiborsiz qoldirildi")

    resolve_as_ignored.short_description = "Flaglarni e'tiborsiz qoldirish"


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ("user", "export_type", "status", "created_at", "expires_at")
    list_filter = ("export_type", "status", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "completed_at", "expires_at")
    actions = ["delete_expired_exports"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Export Details", {"fields": ("export_type", "status", "filters")}),
        ("File", {"fields": ("file", "error_message")}),
        ("Timestamps", {"fields": ("created_at", "completed_at", "expires_at")}),
    )

    def delete_expired_exports(self, request, queryset):
        """Bulk action: Delete expired exports"""
        from django.utils import timezone

        count = queryset.filter(expires_at__lt=timezone.now()).delete()[0]
        self.message_user(request, f"{count} ta muddati o'tgan export o'chirildi")

    delete_expired_exports.short_description = "Muddati o'tgan exportlarni o'chirish"


# Override admin index with custom dashboard
from .admin_dashboard import admin_dashboard

_original_index = admin.site.index
admin.site.index = lambda request, extra_context=None: admin_dashboard(request)
admin.site.site_header = "Fikrly Admin"
admin.site.site_title = "Fikrly Admin"
admin.site.index_title = "Boshqaruv paneli"
