"""Review-related views: submission, editing, deletion, likes, helpful votes."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Avg, Count, F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django_ratelimit.decorators import ratelimit

from ..forms import OwnerResponseForm, ReportReviewForm, ReviewEditForm, ReviewForm
from ..models import ActivityLog, Company, Review
from ..utils import send_telegram_message
from ..visibility import is_company_publicly_visible, public_companies_queryset

logger = logging.getLogger(__name__)


@ensure_csrf_cookie
@login_required
def review_submission(request):
    """Create a new review."""
    preselected_company_id = request.GET.get("company")
    initial = {}
    if preselected_company_id and preselected_company_id.isdigit():
        try:
            initial["company"] = Company.objects.get(pk=int(preselected_company_id), is_active=True)
            if not is_company_publicly_visible(initial["company"]):
                initial.pop("company", None)
        except Company.DoesNotExist:
            pass

    if request.method == "POST":
        def client_key():
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
            ip = ip.split(",")[0].strip() if ip else "unknown"
            return f"review_submission_rl:{request.user.id}:{ip}"

        key = client_key()
        window_seconds = 300
        max_reviews = 15
        entry = cache.get(key)
        if entry is None:
            entry = {"count": 0, "ts": now().timestamp()}
        if now().timestamp() - entry["ts"] > window_seconds:
            entry = {"count": 0, "ts": now().timestamp()}

        if entry["count"] >= max_reviews:
            messages.error(
                request,
                "Siz qisqa vaqt ichida juda ko'p sharh yozdingiz. Iltimos, 5 daqiqadan keyin urinib ko'ring.",
            )
            if preselected_company_id:
                return redirect("company_detail", pk=preselected_company_id)
            return redirect("index")

        form = ReviewForm(request.POST, request.FILES)
        try:
            rating_val = int(request.POST.get("rating", 0))
            if not 1 <= rating_val <= 5:
                form.add_error("rating", "Baho 1 dan 5 gacha bo'lishi kerak.")
        except (TypeError, ValueError):
            form.add_error("rating", "To'g'ri baho kiriting (1-5).")

        if form.is_valid():
            if request.user.is_authenticated:
                selected_company = form.cleaned_data.get("company")
                if selected_company and Review.objects.filter(
                    user=request.user, company=selected_company
                ).exists():
                    messages.error(request, "Siz bu kompaniyaga allaqachon sharh yozdingiz.")
                    return redirect("company_detail", pk=selected_company.pk)

            entry["count"] += 1
            cache.set(key, entry, timeout=window_seconds)

            review: Review = form.save(commit=False)
            review.user = request.user
            review.is_approved = False
            review.approval_requested = True
            review.save()

            company = review.company
            agg = company.reviews.filter(is_approved=True).aggregate(avg=Avg("rating"), cnt=Count("id"))
            company.review_count = int(agg.get("cnt") or 0)
            company.rating = (
                round(float(agg.get("avg") or 0.0), 2) if company.review_count else 0
            )
            company.save(update_fields=["review_count", "rating"])

            try:
                from ..email_notifications import EmailNotificationService
                EmailNotificationService.send_new_review_notification(company, review)
            except Exception:
                pass

            messages.success(
                request,
                "Sharhingiz qabul qilindi va moderator tasdiqlagandan keyin ko'rinadi.",
            )
            return redirect("company_detail", pk=company.pk)
    else:
        if request.user.is_authenticated:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            initial["user_name"] = full_name if full_name else request.user.username
        form = ReviewForm(initial=initial)

    suggested_companies = public_companies_queryset().order_by("-review_count", "-rating", "name")[:20]
    return render(
        request,
        "pages/review_submission.html",
        {"form": form, "suggested_companies": suggested_companies},
    )


@login_required
def manager_review_response(request, pk: int):
    """Allow a company manager to post/edit an owner response under a review."""
    try:
        review = Review.objects.select_related("company").get(pk=pk, company__manager=request.user)
    except Review.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = OwnerResponseForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner_response_at = timezone.now()
            review.save(update_fields=["owner_response_text", "owner_response_at"])
            ActivityLog.objects.create(
                actor=request.user,
                action="owner_responded",
                company=review.company,
                review=review,
                details=f"Owner responded to review #{review.pk}",
            )
            try:
                from ..email_notifications import EmailNotificationService
                EmailNotificationService.send_review_response_notification(
                    review, review.owner_response_text
                )
            except Exception:
                pass
            messages.success(request, "Javob saqlandi.")
            return redirect("company_detail", pk=review.company.pk)
    else:
        form = OwnerResponseForm(instance=review)

    return render(
        request,
        "pages/manager_review_response.html",
        {"form": form, "review": review},
    )


@login_required
def report_review(request, pk: int):
    try:
        review = Review.objects.select_related("company").get(pk=pk)
        if not is_company_publicly_visible(review.company) and not (
            request.user.is_superuser
            or (request.user.is_authenticated and review.company.manager == request.user)
        ):
            raise Http404
    except Review.DoesNotExist:
        raise Http404

    def client_key():
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
        ip = ip.split(",")[0].strip() if ip else "unknown"
        return f"report_rl:{request.user.id}:{ip}"

    key = client_key()
    window_seconds = 60
    max_reports = 3
    entry = cache.get(key)
    if entry is None:
        entry = {"count": 0, "ts": now().timestamp()}
    if now().timestamp() - entry["ts"] > window_seconds:
        entry = {"count": 0, "ts": now().timestamp()}

    if request.method == "POST":
        if entry["count"] >= max_reports:
            messages.error(request, "Juda ko'p urinish. Bir daqiqadan so'ng qayta urinib ko'ring.")
            return redirect("company_detail", pk=review.company.pk)

        form = ReportReviewForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.review = review
            report.reporter = request.user
            report.status = "open"
            report.save()

            entry["count"] += 1
            cache.set(key, entry, timeout=window_seconds)

            reason = dict(report._meta.get_field("reason").choices).get(report.reason, report.reason)
            send_telegram_message(
                f"<b>Yangi shikoyat</b>\n"
                f"Kompaniya: {review.company.name}\n"
                f"Sharh #{review.pk} — {review.rating}⭐\n"
                f"Sabab: {reason}\n"
                f"Matn: {review.text[:200]}"
            )
            messages.success(request, "Shikoyatingiz yuborildi. Rahmat.")
            return redirect("company_detail", pk=review.company.pk)
    else:
        form = ReportReviewForm()

    return render(request, "pages/report_review.html", {"form": form, "review": review})


@login_required
@ratelimit(key="user", rate="20/m", method="POST")
def like_review(request, pk: int):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)

    try:
        review = Review.objects.select_related("company__category_fk").get(pk=pk)
        if not is_company_publicly_visible(review.company):
            raise Http404
    except Review.DoesNotExist:
        raise Http404

    from ..models import ReviewLike

    liked = False
    obj, created = ReviewLike.objects.get_or_create(review=review, user=request.user)
    if created:
        liked = True
        Review.objects.filter(pk=pk).update(like_count=F("like_count") + 1)
    else:
        obj.delete()
        Review.objects.filter(pk=pk, like_count__gt=0).update(like_count=F("like_count") - 1)

    current = Review.objects.filter(pk=pk).values_list("like_count", flat=True).first()
    return JsonResponse({"ok": True, "like_count": int(current or 0), "liked": liked})


@login_required
@ratelimit(key="user", rate="30/m", method="POST")
def vote_review_helpful(request, pk: int):
    """Vote on review helpfulness (helpful/not helpful)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    try:
        review = Review.objects.select_related("company__category_fk").select_for_update().get(pk=pk)
        if not is_company_publicly_visible(review.company):
            return JsonResponse({"success": False, "error": "Not found"}, status=404)
    except Review.DoesNotExist:
        return JsonResponse({"success": False, "error": "Review not found"}, status=404)

    try:
        import json
        data = json.loads(request.body)
        vote_type = data.get("vote_type")

        if vote_type not in ["helpful", "not_helpful"]:
            return JsonResponse({"success": False, "error": "Invalid vote type"}, status=400)

        from ..models import ReviewHelpfulVote
        from django.db import transaction

        with transaction.atomic():
            existing_vote = ReviewHelpfulVote.objects.filter(review=review, user=request.user).first()
            if existing_vote:
                old_type = existing_vote.vote_type
                if old_type != vote_type:
                    if old_type == "helpful":
                        Review.objects.filter(pk=pk, helpful_count__gt=0).update(helpful_count=F("helpful_count") - 1)
                    else:
                        Review.objects.filter(pk=pk, not_helpful_count__gt=0).update(not_helpful_count=F("not_helpful_count") - 1)
                    if vote_type == "helpful":
                        Review.objects.filter(pk=pk).update(helpful_count=F("helpful_count") + 1)
                    else:
                        Review.objects.filter(pk=pk).update(not_helpful_count=F("not_helpful_count") + 1)
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
            else:
                ReviewHelpfulVote.objects.create(review=review, user=request.user, vote_type=vote_type)
                if vote_type == "helpful":
                    Review.objects.filter(pk=pk).update(helpful_count=F("helpful_count") + 1)
                else:
                    Review.objects.filter(pk=pk).update(not_helpful_count=F("not_helpful_count") + 1)

        review.refresh_from_db()

        if vote_type == "helpful":
            try:
                from ..email_notifications import EmailNotificationService
                EmailNotificationService.send_helpful_vote_notification(review, review.helpful_count)
            except Exception:
                pass

        return JsonResponse({
            "success": True,
            "helpful_count": review.helpful_count,
            "not_helpful_count": review.not_helpful_count,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def review_edit(request, pk: int):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        raise Http404

    if review.user_id != request.user.id:
        raise Http404

    if request.method == "POST":
        form = ReviewEditForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False
            review.approval_requested = True
            review.save()
            try:
                from ..utils import send_telegram_review_notification
                send_telegram_review_notification(review)
            except Exception:
                pass
            messages.success(request, "Sharh yangilandi va qayta moderatsiyaga yuborildi.")
            return redirect("user_profile")
    else:
        form = ReviewEditForm(instance=review)

    return render(request, "pages/review_edit.html", {"form": form, "review": review})


@login_required
def review_delete(request, pk: int):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        raise Http404

    if review.user_id != request.user.id:
        raise Http404

    if request.method == "POST":
        review.delete()
        messages.success(request, "Sharh o'chirildi.")
        return redirect("user_profile")

    return render(request, "pages/review_delete_confirm.html", {"review": review})
