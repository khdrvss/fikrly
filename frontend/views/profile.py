"""User profile views: own profile, public profile page."""

import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, Sum
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404

from ..forms import ProfileForm
from ..models import Badge, Review, UserGamification, UserProfile

logger = logging.getLogger(__name__)


@login_required
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = ProfileForm(instance=profile)

    user_reviews = Review.objects.filter(
        Q(user=request.user) | Q(user_name=request.user.username)
    ).select_related("company")

    stats = user_reviews.aggregate(avg_rating=Avg("rating"), total_reviews=Count("id"))
    total_reviews = int(stats.get("total_reviews") or 0)
    avg_rating = float(stats.get("avg_rating") or 0.0)
    unique_companies = user_reviews.values("company").distinct().count()
    helpful_votes = user_reviews.aggregate(total_likes=Sum("like_count"))["total_likes"] or 0

    gamification, _ = UserGamification.objects.get_or_create(user=request.user)
    badges = Badge.objects.filter(user=request.user).order_by("-earned_at")[:5]

    return render(
        request,
        "pages/user_profile.html",
        {
            "form": form,
            "user_reviews": user_reviews,
            "profile": profile,
            "profile_stats": {
                "total_reviews": total_reviews,
                "avg_rating": avg_rating,
                "unique_companies": unique_companies,
                "helpful_votes": helpful_votes,
            },
            "gamification": gamification,
            "badges": badges,
        },
    )


def public_profile(request, username: str):
    """Public profile view showing a user's approved reviews and stats."""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)

    reviews = (
        Review.objects.filter(user=user, is_approved=True)
        .select_related("company")
        .order_by("-created_at")
    )

    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0
    helpful_votes = reviews.aggregate(Sum("like_count"))["like_count__sum"] or 0

    gamification = UserGamification.objects.filter(user=user).first()
    badges = Badge.objects.filter(user=user).order_by("-earned_at")[:5]

    return render(
        request,
        "pages/public_profile.html",
        {
            "profile_user": user,
            "profile": profile,
            "reviews": reviews,
            "stats": {
                "total_reviews": total_reviews,
                "avg_rating": avg_rating,
                "helpful_votes": helpful_votes,
            },
            "gamification": gamification,
            "badges": badges,
        },
    )
