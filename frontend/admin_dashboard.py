"""
Custom admin dashboard with statistics and quick actions.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from frontend.models import (
    Company,
    Review,
    UserProfile,
    ActivityLog,
    ReviewReport,
    CompanyClaim,
    DataExport,
)

User = get_user_model()


@staff_member_required
def admin_dashboard(request):
    """Custom admin index with statistics."""

    # Date ranges
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    # User statistics
    total_users = User.objects.count()
    active_users_7d = User.objects.filter(last_login__gte=last_7_days).count()
    new_users_30d = User.objects.filter(date_joined__gte=last_30_days).count()
    # Note: UserProfile does not have `email_verified` field; use admin approval flag instead
    verified_users = UserProfile.objects.filter(is_approved=True).count()

    # Company statistics
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(is_active=True).count()
    verified_companies = Company.objects.filter(is_verified=True).count()
    pending_verifications = Company.objects.filter(
        verification_requested_at__isnull=False, is_verified=False
    ).count()

    # Review statistics
    total_reviews = Review.objects.count()
    approved_reviews = Review.objects.filter(is_approved=True).count()
    pending_reviews = Review.objects.filter(is_approved=False).count()
    verified_purchase_reviews = Review.objects.filter(verified_purchase=True).count()
    avg_rating = (
        Review.objects.filter(is_approved=True).aggregate(Avg("rating"))["rating__avg"]
        or 0
    )

    # Recent activity
    # Use 'user' FK (Review.user) - 'author' does not exist on Review model
    recent_reviews = Review.objects.select_related("company", "user").order_by(
        "-created_at"
    )[:10]
    recent_companies = Company.objects.select_related("manager").order_by("-id")[:10]
    recent_users = User.objects.order_by("-date_joined")[:10]

    # Pending actions
    pending_reports = ReviewReport.objects.filter(status="pending").count()
    pending_claims = CompanyClaim.objects.filter(status="pending").count()
    pending_exports = DataExport.objects.filter(status="pending").count()

    # Activity log (last 20)
    recent_activity = ActivityLog.objects.select_related(
        "actor", "company", "review"
    ).order_by("-created_at")[:20]

    # Top companies by rating
    top_companies = Company.objects.filter(is_active=True, review_count__gt=0).order_by(
        "-rating", "-review_count"
    )[:5]

    # Growth data (last 7 days)
    growth_data = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_stats = {
            "date": day_start.strftime("%Y-%m-%d"),
            "users": User.objects.filter(
                date_joined__range=(day_start, day_end)
            ).count(),
            "reviews": Review.objects.filter(
                created_at__range=(day_start, day_end)
            ).count(),
            "companies": Company.objects.filter(
                id__isnull=False
            ).count(),  # Placeholder
        }
        growth_data.append(day_stats)

    context = {
        # User stats
        "total_users": total_users,
        "active_users_7d": active_users_7d,
        "new_users_30d": new_users_30d,
        "verified_users": verified_users,
        # Company stats
        "total_companies": total_companies,
        "active_companies": active_companies,
        "verified_companies": verified_companies,
        "pending_verifications": pending_verifications,
        # Review stats
        "total_reviews": total_reviews,
        "approved_reviews": approved_reviews,
        "pending_reviews": pending_reviews,
        "verified_purchase_reviews": verified_purchase_reviews,
        "avg_rating": round(avg_rating, 2),
        # Pending actions
        "pending_reports": pending_reports,
        "pending_claims": pending_claims,
        "pending_exports": pending_exports,
        # Recent activity
        "recent_reviews": recent_reviews,
        "recent_companies": recent_companies,
        "recent_users": recent_users,
        "recent_activity": recent_activity,
        "top_companies": top_companies,
        # Growth data
        "growth_data": growth_data,
    }

    return render(request, "admin/custom_index.html", context)
