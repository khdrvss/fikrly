from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.utils.functional import cached_property
import uuid


def _is_russian_language(lang_code: str | None) -> bool:
    if not lang_code:
        return False
    normalized = lang_code.lower().replace("_", "-")
    return normalized.startswith("ru")


def company_logo_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"company_logos/{filename}"


class BusinessCategory(models.Model):
    COLOR_CHOICES = [
        ("red", "Red"),
        ("orange", "Orange"),
        ("yellow", "Yellow"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("purple", "Purple"),
        ("pink", "Pink"),
        ("gray", "Gray"),
    ]
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon_svg = models.TextField(blank=True, help_text=_("SVG path content"))
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default="gray",
        help_text=_("Kategoriya rangi"),
    )
    is_featured = models.BooleanField(
        default=False, help_text=_("Bosh sahifada ko'rsatish")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Agar o'chirilsa, bu kategoriya va uning barcha kompaniyalari saytda ko'rinmaydi"),
        verbose_name="Faol",
    )

    class Meta:
        verbose_name_plural = "Biznes Kategoriyalar (Filtrlarda ishlatiladi)"
        verbose_name = "Biznes Kategoriya"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("business_list_by_category", kwargs={"category_slug": self.slug})

    @property
    def display_name(self):
        lang = get_language()
        if _is_russian_language(lang) and self.name_ru:
            return self.name_ru
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category_fk = models.ForeignKey(
        BusinessCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    city = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="company_images/", blank=True, null=True)
    # Generated optimized images (WEBP) in multiple sizes
    image_400 = models.ImageField(
        upload_to="company_images/variants/", blank=True, null=True
    )
    image_800 = models.ImageField(
        upload_to="company_images/variants/", blank=True, null=True
    )
    image_1200 = models.ImageField(
        upload_to="company_images/variants/", blank=True, null=True
    )
    logo = models.ImageField(
        upload_to=company_logo_path,
        blank=True,
        null=True,
        help_text=_("Kompaniya logotipi (kvadrat shaklda tavsiya etiladi)"),
    )
    logo_url = models.URLField(
        blank=True, help_text=_("Logo uchun tashqi URL (agar fayl yuklanmasa)")
    )
    logo_url_backup = models.URLField(
        blank=True,
        help_text=_("Logo URL zaxirasi (avtomatik saqlanadi)"),
        editable=False,
    )
    logo_scale = models.PositiveIntegerField(
        default=100,
        help_text=_(
            "Logo masshtabi foizda (masalan: 100 = asl o'lcham, 150 = 1.5x kattalashtirish)"
        ),
    )
    website = models.URLField(
        blank=True, help_text=_("Rasmiy veb-sayt, masalan: https://example.com")
    )
    official_email_domain = models.CharField(
        max_length=100, blank=True, help_text=_("Masalan: example.com (ixtiyoriy)")
    )
    tax_id = models.CharField(
        max_length=32, blank=True, help_text=_("INN/СТИР (ixtiyoriy)")
    )
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(
        max_length=255, blank=True, help_text=_("Mo'ljal (ixtiyoriy)")
    )
    phone_public = models.CharField(max_length=60, blank=True)
    email_public = models.EmailField(blank=True)
    facebook_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    working_hours = models.JSONField(
        blank=True, null=True, help_text=_("Haftalik ish vaqtlari JSON ko'rinishida")
    )
    # Optional: choose a file that already exists in media/company_library
    library_image_path = models.CharField(
        max_length=255, blank=True, help_text=_("Masalan: company_library/mylogo.png")
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="managed_companies",
        on_delete=models.SET_NULL,
    )
    is_verified = models.BooleanField(
        default=False, help_text=_("Tasdiqlangan biznes (admin tomonidan tekshirilgan)")
    )
    verification_requested_at = models.DateTimeField(
        null=True, blank=True, help_text=_("Tasdiqlash so'ralgan sana")
    )
    verification_document = models.FileField(
        upload_to="verification_docs/",
        blank=True,
        null=True,
        help_text=_("Tasdiqlash hujjati (litsenziya, guvohnoma)"),
    )
    verification_notes = models.TextField(
        blank=True, help_text=_("Admin izoh (tasdiqlash sababi)")
    )
    is_active = models.BooleanField(
        default=True, help_text=_("Agar o'chirilsa, saytda ko'rinmaydi")
    )
    # Ownership claim state
    is_claimed = models.BooleanField(
        default=False,
        help_text=_("Biznes egasi tomonidan egallangan va tasdiqlangan"),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="owned_companies",
        on_delete=models.SET_NULL,
        help_text=_("Tasdiqlangan biznes egasi"),
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-review_count", "-rating", "name"]
        indexes = [
            # Basic filtering by active status and sorting
            models.Index(fields=["is_active", "-rating"]),
            models.Index(fields=["is_active", "-review_count"]),
            # Category filtering (most common filter)
            models.Index(fields=["category_fk", "is_active", "-rating"]),
            # City filtering
            models.Index(fields=["city", "is_active"]),
            # Verified filtering
            models.Index(fields=["is_verified", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    def image_url_for_size(self, size: int):
        if size == 400 and self.image_400:
            return getattr(self.image_400, "url", "")
        if size == 800 and self.image_800:
            return getattr(self.image_800, "url", "")
        if size == 1200 and self.image_1200:
            return getattr(self.image_1200, "url", "")
        # fallback to uploaded image or external URL
        return self.display_image_url

    @property
    def image_400_url(self):
        return self.image_url_for_size(400)

    @property
    def image_800_url(self):
        return self.image_url_for_size(800)

    @property
    def image_1200_url(self):
        return self.image_url_for_size(1200)

    def save(self, *args, **kwargs):
        if self.logo_url:
            self.logo_url_backup = self.logo_url

        # If a new image file was uploaded, generate WEBP variants.
        try:
            # detect new upload by checking if `image` has a file-like object
            new_image = (
                getattr(self, "image")
                and hasattr(self.image, "file")
                and getattr(self.image.file, "closed", False) is False
            )
        except Exception:
            new_image = False

        super().save(*args, **kwargs)

        # Post-save: generate variants only when an image exists
        if self.image and new_image:
            try:
                from .utils.images import generate_webp_versions

                files = generate_webp_versions(self.image)
                changed = False
                if 400 in files:
                    fname = f"{self.pk}_400.webp"
                    self.image_400.save(fname, files[400], save=False)
                    changed = True
                if 800 in files:
                    fname = f"{self.pk}_800.webp"
                    self.image_800.save(fname, files[800], save=False)
                    changed = True
                if 1200 in files:
                    fname = f"{self.pk}_1200.webp"
                    self.image_1200.save(fname, files[1200], save=False)
                    changed = True

                if changed:
                    # Avoid recursion by using update_fields on file fields
                    super(Company, self).save(
                        update_fields=["image_400", "image_800", "image_1200"]
                    )
            except Exception:
                # Fail silently — preserve original upload if generation fails
                pass

    @property
    def display_description(self):
        lang = get_language()
        if _is_russian_language(lang) and self.description_ru:
            return self.description_ru
        return self.description

    @cached_property
    def display_logo(self) -> str:
        """Return uploaded logo URL, then external URL, then backup URL."""
        if self.logo:
            try:
                if self.logo.name:
                    return self.logo.url
            except Exception:
                pass
        if self.logo_url:
            return self.logo_url
        return self.logo_url_backup or ""

    @property
    def display_image_url(self) -> str:
        """Return uploaded image url if present, else fallback to image_url."""
        try:
            if self.image and hasattr(self.image, "url"):
                return self.image.url
        except Exception:
            pass
        # If a curated library path exists, serve it under MEDIA_URL
        if self.library_image_path:
            from django.conf import settings

            base = (
                settings.MEDIA_URL.rstrip("/")
                if hasattr(settings, "MEDIA_URL")
                else "/media"
            )
            return f"{base}/{self.library_image_path.lstrip('/')}"
        return self.image_url or ""


class Review(models.Model):
    company = models.ForeignKey(
        Company, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="reviews",
        on_delete=models.SET_NULL,
    )
    user_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    receipt = models.ImageField(
        upload_to="review_receipts/", null=True, blank=True, verbose_name="Xarid cheki"
    )
    # Moderation: show reviews only after admin approves
    is_approved = models.BooleanField(default=False, db_index=True)
    approval_requested = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Owner response
    owner_response_text = models.TextField(blank=True)
    owner_response_at = models.DateTimeField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0, db_index=True)
    not_helpful_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "is_approved", "-created_at"]),
            models.Index(fields=["user", "is_approved", "-created_at"]),
            models.Index(fields=["company", "is_approved", "-helpful_count"]),
        ]
        constraints = [
            # One review per authenticated user per company (NULLs are excluded by the DB)
            models.UniqueConstraint(
                fields=["user", "company"],
                condition=models.Q(user__isnull=False),
                name="unique_review_per_user_per_company",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_name} → {self.company.name} ({self.rating})"


class ReviewLike(models.Model):
    """Per-user like for a Review."""

    review = models.ForeignKey(Review, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="review_likes", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")
        indexes = [models.Index(fields=["review", "user"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Like({self.user_id} -> Review {self.review_id})"


class CompanyLike(models.Model):
    """Per-user like for a Company. Enforces one like per user per company."""

    company = models.ForeignKey(Company, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="company_likes", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "user")
        indexes = [models.Index(fields=["company", "user"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Like({self.user_id} -> {self.company_id})"


class ReviewReport(models.Model):
    REASON_CHOICES = [
        ("spam", "Spam yoki firibgarlik"),
        ("abuse", "Qo‘pol so‘zlar / haqoratomuz"),
        ("false", "Noto‘g‘ri maʼlumot"),
        ("pii", "Shaxsiy maʼlumot oshkor etilgan"),
        ("other", "Boshqa"),
    ]

    STATUS_CHOICES = [
        ("open", "Kutilmoqda"),
        ("resolved", "Hal qilindi"),
        ("rejected", "Rad etildi"),
    ]

    review = models.ForeignKey(
        "Review", related_name="reports", on_delete=models.CASCADE
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="open", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Report #{self.pk} on Review #{self.review_id} ({self.reason})"


class ReviewHelpfulVote(models.Model):
    """Track helpful/not helpful votes on reviews."""

    VOTE_CHOICES = [
        ("helpful", "Helpful"),
        ("not_helpful", "Not Helpful"),
    ]

    review = models.ForeignKey(
        Review, related_name="helpful_votes", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="review_helpful_votes",
        on_delete=models.CASCADE,
    )
    vote_type = models.CharField(max_length=15, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")
        indexes = [models.Index(fields=["review", "user"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id} -> Review {self.review_id} ({self.vote_type})"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    # Admin approval workflow
    is_approved = models.BooleanField(default=False)
    requested_approval_at = models.DateTimeField(
        auto_now_add=True, null=True, blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    username_change_log = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


## Review attachments removed for MVP


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ("company_edit", "Company Edited"),
        ("approval_requested", "Review Approval Requested"),
        ("review_approved", "Review Approved"),
        ("owner_responded", "Owner Responded"),
        ("review_created", "Review Created"),
        ("review_reported", "Review Reported"),
        ("company_claim_requested", "Company Claim Requested"),
        ("company_claim_verified", "Company Claim Verified"),
        ("contact_revealed", "Contact Revealed"),
        ("company_liked", "Company Liked"),
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activities",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    company = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
    )
    review = models.ForeignKey(
        Review,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="activity_logs",
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} by {getattr(self.actor, 'username', 'system')}"


class CompanyClaim(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]
    company = models.ForeignKey(
        Company, related_name="claims", on_delete=models.CASCADE
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="company_claims",
        on_delete=models.CASCADE,
    )
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Claim({self.company.name}) by {self.email} [{self.status}]"


def claim_proof_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"claim_proofs/{uuid.uuid4()}.{ext}"


class BusinessOwnershipClaim(models.Model):
    """Full ownership claim with document proof for moderation approval."""

    POSITION_CHOICES = [
        ("owner", "Egasi (Owner)"),
        ("manager", "Menejer (Manager)"),
        ("other", "Boshqa (Other)"),
    ]

    STATUS_CHOICES = [
        ("pending", "Kutilmoqda"),
        ("approved", "Tasdiqlandi"),
        ("rejected", "Rad etildi"),
    ]

    company = models.ForeignKey(
        Company,
        related_name="ownership_claims",
        on_delete=models.CASCADE,
        verbose_name=_("Kompaniya"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="ownership_claims",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Foydalanuvchi"),
    )

    # Applicant info
    full_name = models.CharField(max_length=200, verbose_name=_("To'liq ism"))
    phone = models.CharField(max_length=30, verbose_name=_("Telefon raqam"))
    email = models.EmailField(verbose_name=_("Email"))
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="owner",
        verbose_name=_("Lavozim"),
    )
    proof_file = models.FileField(
        upload_to=claim_proof_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Tasdiq hujjati"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Izoh"))

    # Moderation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name=_("Holat"),
    )
    rejection_reason = models.TextField(blank=True, verbose_name=_("Rad etish sababi"))
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviewed_ownership_claims",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Ko'rib chiqdi"),
    )

    # Telegram message tracking
    telegram_message_id = models.CharField(max_length=50, blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True)

    # Meta
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Biznes egallash so'rovi"
        verbose_name_plural = "Biznes egallash so'rovlari"
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"OwnershipClaim({self.company.name}) by {self.full_name} [{self.status}]"

    @property
    def proof_file_url(self):
        if self.proof_file:
            try:
                return self.proof_file.url
            except Exception:
                return ""
        return ""


class UserGamification(models.Model):
    """Gamification data for users - levels, XP, badges"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gamification"
    )
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    helpful_votes_received = models.PositiveIntegerField(default=0)
    companies_reviewed = models.PositiveIntegerField(default=0)

    # Streak tracking
    current_streak = models.PositiveIntegerField(
        default=0, help_text="Consecutive days with activity"
    )
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Gamification"
        verbose_name_plural = "User Gamifications"

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"

    @property
    def next_level_xp(self):
        """Calculate XP needed for next level"""
        return self.level * 100  # 100 XP per level

    @property
    def xp_progress(self):
        """Calculate progress to next level (0-100)"""
        current_level_xp = (self.level - 1) * 100
        xp_in_level = self.xp - current_level_xp
        return min(100, (xp_in_level / 100) * 100)

    def add_xp(self, amount, reason=""):
        """Add XP and level up if needed"""
        self.xp += amount

        # Check for level up
        while self.xp >= self.next_level_xp:
            self.level += 1
            # Award badge for level milestones
            if self.level in [5, 10, 25, 50, 100]:
                Badge.objects.get_or_create(
                    user=self.user,
                    badge_type=f"level_{self.level}",
                    defaults={
                        "name": f"Level {self.level} Master",
                        "description": f"Reached level {self.level}",
                        "icon": "🎯",
                    },
                )

        self.save()

    def update_streak(self):
        """Update activity streak"""
        from datetime import date, timedelta

        today = date.today()

        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days

            if days_diff == 1:
                # Consecutive day
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
            elif days_diff > 1:
                # Streak broken
                self.current_streak = 1
            # Same day - no change
        else:
            self.current_streak = 1

        self.last_activity_date = today
        self.save()


class Badge(models.Model):
    """Achievement badges for users"""

    BADGE_TYPES = [
        ("first_review", "First Review"),
        ("helpful_10", "10 Helpful Votes"),
        ("helpful_50", "50 Helpful Votes"),
        ("helpful_100", "100 Helpful Votes"),
        ("reviews_10", "10 Reviews"),
        ("reviews_50", "50 Reviews"),
        ("reviews_100", "100 Reviews"),
        ("streak_7", "7 Day Streak"),
        ("streak_30", "30 Day Streak"),
        ("level_5", "Level 5"),
        ("level_10", "Level 10"),
        ("level_25", "Level 25"),
        ("verified", "Verified Reviewer"),
        ("expert", "Category Expert"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🏆")
    earned_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True, help_text="Show as new notification")

    class Meta:
        unique_together = ["user", "badge_type"]
        ordering = ["-earned_at"]
        verbose_name = "Badge"
        verbose_name_plural = "Badges"

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class ReviewImage(models.Model):
    """Images attached to reviews"""

    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="review_images/",
        help_text="Review image (will be compressed automatically)",
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "uploaded_at"]
        verbose_name = "Review Image"
        verbose_name_plural = "Review Images"

    def __str__(self):
        return f"Image for review {self.review.id}"


class ReviewFlag(models.Model):
    """Flagged reviews for moderation"""

    FLAG_REASONS = [
        ("spam", "Spam"),
        ("fake", "Fake Review"),
        ("inappropriate", "Inappropriate Content"),
        ("offensive", "Offensive Language"),
        ("duplicate", "Duplicate Review"),
        ("other", "Other"),
    ]

    review = models.ForeignKey("Review", on_delete=models.CASCADE, related_name="flags")
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flagged_reviews",
    )
    reason = models.CharField(max_length=20, choices=FLAG_REASONS)
    description = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_flags",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    action_taken = models.CharField(
        max_length=100,
        blank=True,
        help_text="What action was taken (deleted, approved, warned)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review Flag"
        verbose_name_plural = "Review Flags"

    def __str__(self):
        return f"Flag: {self.review.id} - {self.reason}"


class DataExport(models.Model):
    """Track data export requests"""

    EXPORT_TYPES = [
        ("reviews_pdf", "Reviews PDF"),
        ("reviews_excel", "Reviews Excel"),
        ("user_data", "User Data (GDPR)"),
        ("business_data", "Business Data"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="data_exports"
    )
    export_type = models.CharField(max_length=20, choices=EXPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file = models.FileField(upload_to="exports/", blank=True, null=True)
    filters = models.JSONField(
        default=dict, help_text="Export filters (company_id, date_range, etc.)"
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="File auto-deletes after this date (7 days)"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Data Export"
        verbose_name_plural = "Data Exports"

    def __str__(self):
        return f"{self.user.username} - {self.export_type} - {self.status}"
