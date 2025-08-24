from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered
from .models import Company, Review


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "city", "rating", "review_count", "is_verified")
    list_filter = ("category", "city", "is_verified")
    search_fields = ("name", "city", "category")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("company", "user_name", "rating", "verified_purchase", "created_at")
    list_filter = ("rating", "verified_purchase", "company")
    search_fields = ("company__name", "user_name", "text")

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
