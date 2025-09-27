from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='company_images/', blank=True, null=True)
    website = models.URLField(blank=True, help_text="Rasmiy veb-sayt, masalan: https://example.com")
    official_email_domain = models.CharField(max_length=100, blank=True, help_text="Masalan: example.com (ixtiyoriy)")
    tax_id = models.CharField(max_length=32, blank=True, help_text="INN/СТИР (ixtiyoriy)")
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=255, blank=True, help_text="Mo'ljal (ixtiyoriy)")
    phone_public = models.CharField(max_length=60, blank=True)
    email_public = models.EmailField(blank=True)
    facebook_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    working_hours = models.JSONField(blank=True, null=True, help_text="Haftalik ish vaqtlari JSON ko'rinishida")
    # Optional: choose a file that already exists in media/company_library
    library_image_path = models.CharField(max_length=255, blank=True, help_text="Masalan: company_library/mylogo.png")
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='managed_companies', on_delete=models.SET_NULL)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_count', '-rating', 'name']

    def __str__(self) -> str:
        return self.name

    @property
    def display_image_url(self) -> str:
        """Return uploaded image url if present, else fallback to image_url."""
        try:
            if self.image and hasattr(self.image, 'url'):
                return self.image.url
        except Exception:
            pass
        # If a curated library path exists, serve it under MEDIA_URL
        if self.library_image_path:
            from django.conf import settings
            base = settings.MEDIA_URL.rstrip('/') if hasattr(settings, 'MEDIA_URL') else '/media'
            return f"{base}/{self.library_image_path.lstrip('/')}"
        return self.image_url or ''


class Review(models.Model):
    company = models.ForeignKey(Company, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='reviews', on_delete=models.SET_NULL)
    user_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    verified_purchase = models.BooleanField(default=True)
    # Moderation: show reviews only after admin approves
    is_approved = models.BooleanField(default=False, db_index=True)
    approval_requested = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Owner response
    owner_response_text = models.TextField(blank=True)
    owner_response_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user_name} → {self.company.name} ({self.rating})"


class CompanyLike(models.Model):
    """Per-user like for a Company. Enforces one like per user per company."""
    company = models.ForeignKey(Company, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='company_likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'user')
        indexes = [models.Index(fields=['company', 'user'])]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Like({self.user_id} -> {self.company_id})"


class ReviewReport(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam yoki firibgarlik'),
        ('abuse', 'Qo‘pol so‘zlar / haqoratomuz'),
        ('false', 'Noto‘g‘ri maʼlumot'),
        ('pii', 'Shaxsiy maʼlumot oshkor etilgan'),
        ('other', 'Boshqa'),
    ]

    STATUS_CHOICES = [
        ('open', 'Kutilmoqda'),
        ('resolved', 'Hal qilindi'),
        ('rejected', 'Rad etildi'),
    ]

    review = models.ForeignKey('Review', related_name='reports', on_delete=models.CASCADE)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Report #{self.pk} on Review #{self.review_id} ({self.reason})"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    # Admin approval workflow
    is_approved = models.BooleanField(default=False)
    requested_approval_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


## Review attachments removed for MVP


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('company_edit', 'Company Edited'),
        ('approval_requested', 'Review Approval Requested'),
    ('review_approved', 'Review Approved'),
    ('owner_responded', 'Owner Responded'),
    ('review_created', 'Review Created'),
    ('review_reported', 'Review Reported'),
    ('company_claim_requested', 'Company Claim Requested'),
    ('company_claim_verified', 'Company Claim Verified'),
    ('contact_revealed', 'Contact Revealed'),
    ('company_liked', 'Company Liked'),
    )
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='activity_logs')
    review = models.ForeignKey(Review, null=True, blank=True, on_delete=models.SET_NULL, related_name='activity_logs')
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} by {getattr(self.actor, 'username', 'system')}"


class PhoneOTP(models.Model):
    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['phone', 'created_at'])]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"OTP({self.phone}) {self.code}"


class CompanyClaim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    company = models.ForeignKey(Company, related_name='claims', on_delete=models.CASCADE)
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='company_claims', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    request_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Claim({self.company.name}) by {self.email} [{self.status}]"


class Category(models.Model):
    COLOR_CHOICES = [
        ('red', 'Qizil'),
        ('orange', 'To\'q sariq'),
        ('yellow', 'Sariq'),
        ('green', 'Yashil'),
        ('blue', 'Ko\'k'),
        ('purple', 'Binafsha'),
        ('pink', 'Pushti'),
        ('gray', 'Kulrang'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL slug")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    icon_svg = models.TextField(blank=True, verbose_name="SVG icon kodi", help_text="SVG path elementi, masalan: <path d='M12 2L2 7L12 12L22 7L12 2Z'/>")
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='gray', verbose_name="Rang")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Tartib", help_text="Kichik raqam birinchi ko'rsatiladi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
    
    def __str__(self):
        return self.name
    
    @property
    def company_count(self):
        """Return count of companies in this category"""
        return Company.objects.filter(category=self.name).count()
    
    @property
    def review_count(self):
        """Return total reviews for companies in this category"""
        from django.db.models import Sum
        result = Company.objects.filter(category=self.name).aggregate(
            total_reviews=Sum('review_count')
        )
        return result['total_reviews'] or 0
