"""
Advanced features views: Analytics, Gamification, 2FA
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Company, Review, UserGamification, Badge, ReviewImage, BusinessCategory
from .visibility import public_companies_queryset
import json


@login_required
def analytics_dashboard(request, company_id):
    """Analytics dashboard for company owners"""
    company = get_object_or_404(Company, id=company_id, manager=request.user)

    # Date range filter
    days = int(request.GET.get("days", 30))
    start_date = timezone.now() - timedelta(days=days)

    # Reviews in period
    reviews = Review.objects.filter(
        company=company, created_at__gte=start_date, is_approved=True
    )

    # Basic stats
    stats = {
        "total_reviews": company.review_count,
        "average_rating": float(company.rating),
        "new_reviews": reviews.count(),
        "response_rate": calculate_response_rate(company),
        "helpful_reviews": reviews.filter(helpful_count__gte=5).count(),
    }

    # Rating distribution
    rating_distribution = list(
        reviews.values("rating").annotate(count=Count("id")).order_by("rating")
    )

    # Reviews over time (daily)
    reviews_over_time = []
    for i in range(days):
        date = timezone.now() - timedelta(days=i)
        count = reviews.filter(created_at__date=date.date()).count()
        reviews_over_time.append({"date": date.strftime("%Y-%m-%d"), "count": count})
    reviews_over_time.reverse()

    # Top reviews (most helpful)
    top_reviews = reviews.order_by("-helpful_count")[:5]

    # Recent reviews needing response
    pending_responses = Review.objects.filter(
        company=company, is_approved=True, owner_response_text=""
    ).order_by("-created_at")[:10]

    context = {
        "company": company,
        "stats": stats,
        "rating_distribution": json.dumps(rating_distribution),
        "reviews_over_time": json.dumps(reviews_over_time),
        "top_reviews": top_reviews,
        "pending_responses": pending_responses,
        "days": days,
    }

    return render(request, "frontend/analytics_dashboard.html", context)


def calculate_response_rate(company):
    """Calculate percentage of reviews with owner responses"""
    total = company.review_count
    if total == 0:
        return 0

    responded = (
        Review.objects.filter(company=company, is_approved=True)
        .exclude(owner_response_text="")
        .count()
    )

    return round((responded / total) * 100, 1)


@login_required
def user_gamification_profile(request):
    """User's gamification profile with levels, XP, badges"""
    gamification, created = UserGamification.objects.get_or_create(user=request.user)

    # Get user badges
    badges = Badge.objects.filter(user=request.user)
    new_badges = badges.filter(is_new=True)

    # Mark badges as seen
    if new_badges.exists():
        new_badges.update(is_new=False)

    # Leaderboard (top 10 users by XP)
    leaderboard = UserGamification.objects.select_related("user").order_by("-xp")[:10]

    # Available badges to earn
    all_badge_types = dict(Badge.BADGE_TYPES)
    earned_types = set(badges.values_list("badge_type", flat=True))
    available_badges = [
        {"type": k, "name": v}
        for k, v in all_badge_types.items()
        if k not in earned_types
    ]

    context = {
        "gamification": gamification,
        "badges": badges,
        "new_badges": new_badges,
        "leaderboard": leaderboard,
        "available_badges": available_badges,
    }

    return render(request, "frontend/gamification_profile.html", context)


def advanced_search(request):
    """Advanced search with filters"""
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    city = request.GET.get("city", "")
    min_rating = request.GET.get("min_rating", "")
    sort_by = request.GET.get("sort", "rating")

    companies = public_companies_queryset()

    # Apply filters
    if query:
        companies = companies.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category_fk__name__icontains=query)
        )

    if category:
        companies = companies.filter(
            Q(category_fk__name__icontains=category)
        )

    if city:
        companies = companies.filter(city__icontains=city)

    if min_rating:
        companies = companies.filter(rating__gte=float(min_rating))

    # Sorting
    if sort_by == "rating":
        companies = companies.order_by("-rating", "-review_count")
    elif sort_by == "reviews":
        companies = companies.order_by("-review_count")
    elif sort_by == "newest":
        companies = companies.order_by("-id")
    elif sort_by == "name":
        companies = companies.order_by("name")

    # Build filter options from the current result set
    categories = (
        BusinessCategory.objects.filter(companies__in=companies)
        .distinct()
        .values_list("name", flat=True)
    )
    cities = companies.exclude(city="").values_list("city", flat=True).distinct()

    context = {
        "companies": companies,
        "query": query,
        "selected_category": category,
        "selected_city": city,
        "selected_rating": min_rating,
        "sort_by": sort_by,
        "categories": categories,
        "cities": cities,
    }

    return render(request, "frontend/advanced_search.html", context)


@login_required
def upload_review_images(request, review_id):
    """Upload multiple images for a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        images = request.FILES.getlist("images")

        for idx, image in enumerate(images[:5]):  # Max 5 images
            ReviewImage.objects.create(review=review, image=image, order=idx)

        return JsonResponse(
            {
                "success": True,
                "count": len(images),
                "message": f"{len(images)} rasmlar yuklandi",
            }
        )

    return JsonResponse({"success": False, "error": "Invalid request"})
