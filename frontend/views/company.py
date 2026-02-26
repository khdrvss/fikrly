"""Company-related views: listings, detail, dashboard, claims, likes."""

import json
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, F, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django_ratelimit.decorators import ratelimit

from ..forms import (
    BusinessOwnershipClaimForm,
    ClaimCompanyForm,
    CompanyManagerEditForm,
    ReviewApprovalRequestForm,
)
from ..models import (
    ActivityLog,
    BusinessCategory,
    BusinessOwnershipClaim,
    Company,
    CompanyClaim,
    CompanyLike,
    Review,
)
from ..utils import (
    compute_assessment,
    diff_instance_fields,
    send_telegram_message,
    send_ownership_claim_notification,
    edit_telegram_message,
    answer_telegram_callback,
)
from ..visibility import (
    is_company_publicly_visible,
    public_companies_queryset,
    visible_business_categories,
)

try:
    from django.contrib.postgres.search import (
        SearchQuery,
        SearchRank,
        SearchVector,
        TrigramSimilarity,
    )
except ImportError:
    SearchQuery = SearchRank = SearchVector = TrigramSimilarity = None

logger = logging.getLogger(__name__)


def home(request):
    _is_anon_get = request.method == "GET" and not request.user.is_authenticated
    _home_cache_key = None
    if _is_anon_get:
        from django.utils.translation import get_language
        _home_cache_key = f"home_page:{get_language()}"
        _cached = cache.get(_home_cache_key)
        if _cached is not None:
            _resp = HttpResponse(_cached)
            _resp["Vary"] = "Accept-Language"
            return _resp

    top_companies = public_companies_queryset().select_related("category_fk").order_by("-rating")[:6]
    trending = public_companies_queryset().select_related("category_fk").order_by("-review_count")[:6]
    latest_reviews = (
        Review.objects.filter(company__in=public_companies_queryset())
        .select_related("company", "user")
        .order_by("-created_at")[:6]
    )
    featured_categories = (
        visible_business_categories(BusinessCategory.objects.all())
        .annotate(company_count=Count("companies", filter=Q(companies__is_active=True)))
        .order_by("-company_count")[:4]
    )
    for c in trending:
        c.assessment = compute_assessment(float(c.rating), int(c.review_count))

    ctx = {
        "top_companies": top_companies,
        "trending_companies": trending,
        "latest_reviews": latest_reviews,
        "featured_categories": featured_categories,
        "canonical_url": request.build_absolute_uri(),
    }
    if request.user.is_authenticated and not request.session.get("_redirected_once"):
        request.session["_next_after_login"] = request.session.get("_next_after_login", "/profile/")
        request.session["_redirected_once"] = True

    response = render(request, "pages/home.html", ctx)
    response["Vary"] = "Accept-Language"
    if _is_anon_get and _home_cache_key:
        cache.set(_home_cache_key, response.content, 60 * 5)
    return response


def homepage(request):
    """Legacy alias for home."""
    return render(request, "pages/home.html")


@login_required
def business_dashboard(request):
    companies = Company.objects.filter(manager=request.user)
    pending_reviews = Review.objects.filter(
        company__manager=request.user, is_approved=False
    ).select_related("company")

    stats = companies.aggregate(
        total_reviews=Sum("review_count"),
        avg_rating=Avg("rating"),
        total_likes=Sum("like_count"),
        total_views=Sum("view_count"),
    )
    contact_clicks = ActivityLog.objects.filter(
        company__in=companies, action="contact_revealed"
    ).count()
    stats["total_clicks"] = contact_clicks

    from django.db.models.functions import TruncDay

    days_30_ago = now() - timedelta(days=29)
    daily_reviews = (
        Review.objects.filter(company__in=companies, created_at__gte=days_30_ago)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    daily_clicks = (
        ActivityLog.objects.filter(
            company__in=companies, action="contact_revealed", created_at__gte=days_30_ago
        )
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    chart_data = {}
    for i in range(30):
        d = (now() - timedelta(days=i)).date()
        chart_data[d] = {"reviews": 0, "clicks": 0}
    for entry in daily_reviews:
        if entry["day"]:
            d = entry["day"].date()
            if d in chart_data:
                chart_data[d]["reviews"] = entry["count"]
    for entry in daily_clicks:
        if entry["day"]:
            d = entry["day"].date()
            if d in chart_data:
                chart_data[d]["clicks"] = entry["count"]

    sorted_dates = sorted(chart_data.keys())
    chart_labels = [d.strftime("%d.%m") for d in sorted_dates]
    chart_reviews = [chart_data[d]["reviews"] for d in sorted_dates]
    chart_clicks = [chart_data[d]["clicks"] for d in sorted_dates]

    return render(
        request,
        "pages/manager_dashboard.html",
        {
            "companies": companies,
            "pending_reviews": pending_reviews,
            "stats": stats,
            "chart_labels": json.dumps(chart_labels),
            "chart_reviews": json.dumps(chart_reviews),
            "chart_clicks": json.dumps(chart_clicks),
        },
    )


def business_profile(request):
    """Redirect to business list — shows all businesses as cards."""
    return redirect("business_list")


@login_required
def manager_company_edit(request, pk: int):
    try:
        company = Company.objects.get(pk=pk, manager=request.user)
    except Company.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = CompanyManagerEditForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            obj = form.save()
            changed = {k: form.cleaned_data.get(k) for k in form.changed_data}
            ActivityLog.objects.create(
                actor=request.user,
                action="company_edit",
                company=obj,
                details=diff_instance_fields(obj, changed),
            )
            messages.success(request, _("Company information updated."))
            return redirect("business_dashboard")
    else:
        form = CompanyManagerEditForm(instance=company)

    return render(
        request,
        "pages/manager_company_edit.html",
        {"form": form, "company": company},
    )


@login_required
def manager_request_approval(request, pk: int):
    try:
        review = Review.objects.select_related("company").get(
            pk=pk, company__manager=request.user
        )
    except Review.DoesNotExist:
        raise Http404

    if request.method == "POST":
        form = ReviewApprovalRequestForm(request.POST)
        if form.is_valid():
            review.approval_requested = True
            review.save(update_fields=["approval_requested"])
            ActivityLog.objects.create(
                actor=request.user,
                action="approval_requested",
                company=review.company,
                review=review,
                details=f"Review #{review.pk} approval requested",
            )
            send_telegram_message(
                f"<b>Approval requested</b>\n"
                f"Company: {review.company.name}\n"
                f"By: {request.user.username}\n"
                f"Review #{review.pk} — {review.rating}⭐\n"
                f"{review.text[:180]}..."
            )
            messages.success(request, "Tasdiqlash so'rovi yuborildi. Adminlar ko'rib chiqishadi.")
            return redirect("business_dashboard")
    else:
        form = ReviewApprovalRequestForm()

    return render(
        request,
        "pages/manager_request_approval.html",
        {"form": form, "review": review},
    )


@ratelimit(key="ip", rate="30/m", method="GET")
def search_suggestions_api(request):
    """API endpoint for live search suggestions."""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    from django.utils.translation import get_language
    cache_key = f"api:search_suggestions:{get_language()}:{query.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse({"results": cached})

    companies = (
        public_companies_queryset()
        .filter(Q(name__icontains=query) | Q(description__icontains=query))
        .select_related("category_fk")
        .only(
            "id", "name", "category_fk", "logo", "logo_url",
            "logo_scale", "image", "image_url", "library_image_path",
        )
        .order_by("-rating")[:8]
    )

    results = [
        {
            "type": "company",
            "id": c.id,
            "name": c.name,
            "category": c.category_fk.display_name if c.category_fk else "",
            "logo": c.display_logo,
            "image": c.display_image_url,
            "logo_scale": c.logo_scale,
            "url": reverse("company_detail", args=[c.id]),
        }
        for c in companies
    ]
    cache.set(cache_key, results, 60 * 5)
    return JsonResponse({"results": results})


def business_list(request, category_slug=None):
    """View that lists all businesses as clickable cards with enhanced search."""
    companies = (
        public_companies_queryset()
        .select_related("category_fk")
        .only(
            "id", "name", "city", "created_at", "description", "description_ru",
            "image", "image_800", "image_url", "library_image_path",
            "logo", "logo_url", "logo_url_backup", "logo_scale",
            "is_verified", "rating", "review_count",
            "category_fk", "category_fk__id", "category_fk__name",
            "category_fk__name_ru", "category_fk__slug",
        )
    )

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    is_get = request.method.upper() == "GET"
    use_cache = is_get and (not request.user.is_authenticated) and (not is_ajax)
    cache_key = None
    if use_cache:
        from django.utils.translation import get_language
        cache_key = f"business_list:{get_language()}:{request.get_full_path()}"
        cached_html = cache.get(cache_key)
        if cached_html:
            return HttpResponse(cached_html)

    query = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    categories_multi = request.GET.getlist("categories")
    if categories_multi:
        cat_vals = []
        for item in categories_multi:
            cat_vals.extend([v.strip() for v in str(item).split(",") if v.strip()])
    else:
        categories_param = request.GET.get("categories", "").strip()
        cat_vals = [v.strip() for v in categories_param.split(",") if v.strip()]
    min_rating = request.GET.get("min_rating")
    verified = request.GET.get("verified")
    sort = request.GET.get("sort", "top")

    if category_slug:
        category_filter = category_slug
    else:
        category_filter = request.GET.get("category", "").strip()

    if query:
        from django.db import connection
        if connection.vendor == "postgresql":
            search_vector = (
                SearchVector("name", weight="A")
                + SearchVector("description", weight="B")
                + SearchVector("city", weight="C")
            )
            search_query = SearchQuery(query, search_type="websearch")
            companies = (
                companies.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
                .filter(
                    Q(search=search_query)
                    | Q(name__icontains=query)
                    | Q(city__icontains=query)
                    | Q(category_fk__name__icontains=query)
                    | Q(category_fk__name_ru__icontains=query)
                )
                .order_by("-rank", "-review_count", "-rating")
            )
            if not companies.exists():
                companies = (
                    public_companies_queryset()
                    .select_related("category_fk")
                    .only(
                        "id", "name", "city", "created_at", "description", "description_ru",
                        "image", "image_800", "image_url", "library_image_path",
                        "logo", "logo_url", "logo_url_backup", "logo_scale",
                        "is_verified", "rating", "review_count", "category_fk",
                    )
                    .annotate(similarity=TrigramSimilarity("name", query))
                    .filter(similarity__gt=0.3)
                    .order_by("-similarity")
                )
        else:
            companies = companies.filter(
                Q(name__icontains=query)
                | Q(city__icontains=query)
                | Q(category_fk__name__icontains=query)
                | Q(category_fk__name_ru__icontains=query)
                | Q(description__icontains=query)
            ).order_by("-review_count", "-rating", "name")

    category_display_name = category_filter
    if category_filter:
        cat_obj = visible_business_categories(BusinessCategory.objects.all()).filter(
            slug=category_filter
        ).first()
        if cat_obj:
            companies = companies.filter(category_fk=cat_obj)
            category_display_name = cat_obj.display_name
        else:
            companies = companies.none()

    if cat_vals:
        id_vals = [v for v in cat_vals if v.isdigit()]
        slug_vals = [v for v in cat_vals if not v.isdigit()]
        qcats = Q()
        if id_vals:
            qcats |= Q(category_fk__id__in=[int(x) for x in id_vals])
        if slug_vals:
            qcats |= Q(category_fk__slug__in=slug_vals)
        companies = companies.filter(qcats)

    if city:
        companies = companies.filter(Q(city__iexact=city) | Q(city__icontains=city))

    if verified is not None and verified != "":
        try:
            if int(verified) == 1:
                companies = companies.filter(is_verified=True)
            else:
                companies = companies.filter(is_verified=False)
        except Exception:
            pass

    if min_rating:
        try:
            companies = companies.filter(rating__gte=float(min_rating))
        except Exception:
            pass

    if sort == "top":
        companies = companies.order_by("-rating", "-review_count", "name")
    elif sort == "new":
        companies = companies.order_by("-created_at")
    elif sort == "most_reviews":
        companies = companies.order_by("-review_count")
    elif sort == "az":
        companies = companies.order_by("name")
    else:
        companies = companies.order_by("-rating", "-review_count", "name")

    if (
        not query
        and not cat_vals
        and not city
        and not min_rating
        and (verified is None or verified == "")
    ):
        companies = companies.order_by("-review_count", "-rating", "name")

    search_suggestions = []
    search_context = query or category_display_name
    search_display = (
        query if query
        else f"Kategoriya: {category_display_name}" if category_filter
        else ""
    )

    total_count = companies.count()
    paginator = Paginator(companies, 20)
    page_number = request.GET.get("page", 1)
    logger.debug("business_list requested page: %s; total_companies=%s", page_number, total_count)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if (query or category_filter) and total_count == 0:
        popular_categories = (
            visible_business_categories(BusinessCategory.objects.all())
            .annotate(count=Count("companies", filter=Q(companies__is_active=True)))
            .order_by("-count")[:5]
            .values_list("name", flat=True)
        )
        popular_cities = (
            public_companies_queryset().values_list("city", flat=True).distinct()[:5]
        )
        search_suggestions = {
            "categories": list(popular_categories),
            "cities": list(popular_cities),
        }

    from django.utils.translation import get_language
    current_lang = get_language() or "uz"
    filter_cache_key = f"business_list:filters:{current_lang}"
    filter_data = cache.get(filter_cache_key)
    if filter_data is None:
        filter_data = {
            "all_categories": list(
                visible_business_categories(BusinessCategory.objects.all())
                .annotate(company_count=Count("companies", filter=Q(companies__is_active=True)))
                .order_by("name")
            ),
            "all_cities": list(
                public_companies_queryset()
                .values_list("city", flat=True)
                .distinct()
                .order_by("city")
            ),
        }
        cache.set(filter_cache_key, filter_data, 60 * 10)

    ctx = {
        "companies": page_obj,
        "page_obj": page_obj,
        "search_query": search_context,
        "search_results_count": total_count,
        "category_filter": category_display_name,
        "search_display": search_display,
        "search_suggestions": search_suggestions,
        "canonical_url": request.build_absolute_uri(),
        "all_categories": filter_data["all_categories"],
        "all_cities": filter_data["all_cities"],
        "selected_filters": {
            "q": query,
            "city": city,
            "categories": cat_vals,
            "min_rating": min_rating,
            "verified": verified,
            "sort": sort,
        },
    }

    if use_cache and cache_key:
        from django.template.loader import render_to_string
        rendered = render_to_string("pages/business_list.html", ctx, request=request)
        cache.set(cache_key, rendered, 60 * 5)
        return HttpResponse(rendered)

    return render(request, "pages/business_list.html", ctx)


def category_browse(request):
    categories = (
        visible_business_categories(BusinessCategory.objects.all())
        .annotate(
            company_count=Count("companies", filter=Q(companies__is_active=True)),
            review_count=Count("companies__reviews", filter=Q(companies__is_active=True)),
        )
        .filter(company_count__gt=0)
        .order_by("name")
    )
    cat_list = [
        {
            "category": cat.slug,
            "label": cat.display_name,
            "icon": cat.icon_svg,
            "color": cat.color,
            "review_count": cat.review_count,
            "company_count": cat.company_count,
            "avg_rating": 0,
        }
        for cat in categories
    ]
    return render(request, "pages/category_browse.html", {"categories": cat_list})


@login_required
def claim_company(request, pk: int):
    try:
        company = Company.objects.get(pk=pk)
        if not is_company_publicly_visible(company) and not request.user.is_superuser:
            raise Http404
    except Company.DoesNotExist:
        raise Http404

    if company.manager_id and company.manager_id != request.user.id:
        messages.error(request, "Bu kompaniya allaqon boshqarilmoqda.")
        return redirect("company_detail", pk=company.pk)

    if request.method == "POST":
        form = ClaimCompanyForm(request.POST, company=company)
        if form.is_valid():
            email = form.cleaned_data["email"]
            token = get_random_string(48)
            exp = now() + timedelta(hours=24)
            ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
            ua = request.META.get("HTTP_USER_AGENT", "")[:500]
            claim = CompanyClaim.objects.create(
                company=company,
                claimant=request.user,
                email=email,
                token=token,
                expires_at=exp,
                request_ip=(ip.split(",")[0].strip() if ip else None),
                user_agent=ua,
            )
            ActivityLog.objects.create(
                actor=request.user,
                action="company_claim_requested",
                company=company,
                details=f"Claim requested by {request.user.username} with {email}",
            )
            try:
                from django.conf import settings as dj_settings
                send_telegram_message(
                    f"🏢 New company claim request\n"
                    f"Company: {company.name}\n"
                    f"User: {request.user.username}\n"
                    f"Email: {email}\n"
                    f"Claim ID: {claim.id}",
                    chat_ids=dj_settings.TELEGRAM_ADMIN_CHAT_IDS,
                )
            except Exception:
                pass

            verify_url = request.build_absolute_uri(reverse("verify_claim", args=[token]))
            body = (
                f"Salom,\n\nSiz {company.name} kompaniyasini tasdiqlash uchun so'rov yubordingiz.\n"
                f"Quyidagi havola orqali 24 soat ichida tasdiqlang:\n{verify_url}\n\nRahmat."
            )
            try:
                send_mail("Kompaniya tasdiqlash havolasi", body, None, [email], fail_silently=True)
            except Exception:
                pass

            messages.success(request, "Tasdiqlash havolasi email manzilingizga yuborildi.")
            return redirect("company_detail", pk=company.pk)
    else:
        form = ClaimCompanyForm(company=company)

    return render(request, "pages/company_claim.html", {"company": company, "form": form})


def verify_claim(request, token: str):
    try:
        claim = CompanyClaim.objects.select_related("company", "claimant").get(token=token)
    except CompanyClaim.DoesNotExist:
        raise Http404

    if claim.status != "pending":
        messages.info(request, "Bu so'rov allaqon ko'rib chiqilgan.")
        return redirect("company_detail", pk=claim.company.pk)

    if now() > claim.expires_at:
        claim.status = "expired"
        claim.save(update_fields=["status"])
        messages.error(request, "Tasdiqlash havolasi muddati tugagan.")
        return redirect("company_detail", pk=claim.company.pk)

    company = claim.company
    company.manager = claim.claimant
    company.is_verified = True
    company.save(update_fields=["manager", "is_verified"])
    claim.status = "verified"
    claim.verified_at = now()
    claim.save(update_fields=["status", "verified_at"])
    ActivityLog.objects.create(
        actor=claim.claimant,
        action="company_claim_verified",
        company=company,
        details=f"Claim verified for {company.name} by {claim.claimant.username}",
    )
    messages.success(request, _("Company verified and linked to your profile."))
    return redirect("company_detail", pk=company.pk)


def verification_badge(request):
    return render(request, "pages/verification_badge.html")


# ─────────────────────────────────────────────
# NEW: Full ownership claim flow
# ─────────────────────────────────────────────

@ratelimit(key="ip", rate="3/h", method="POST", block=True)
def submit_ownership_claim(request, pk: int):
    """AJAX endpoint: receive ownership claim form, save, notify Telegram."""
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)

    company = get_object_or_404(Company, pk=pk)
    if not is_company_publicly_visible(company) and not getattr(request.user, "is_superuser", False):
        return JsonResponse({"ok": False, "error": "Not found"}, status=404)

    # Check for existing pending claim on this business
    if BusinessOwnershipClaim.objects.filter(company=company, status="pending").exists():
        return JsonResponse({
            "ok": False,
            "error": "Bu biznes uchun allaqon so'rov mavjud. Admin ko'rib chiqmoqda."
        }, status=400)

    # If business is already claimed
    if company.is_claimed:
        return JsonResponse({
            "ok": False,
            "error": "Bu biznes allaqon tasdiqlangan egaga ega."
        }, status=400)

    form = BusinessOwnershipClaimForm(request.POST, request.FILES, company=company)
    if not form.is_valid():
        errors = {f: e.as_text() for f, e in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
    claim = BusinessOwnershipClaim.objects.create(
        company=company,
        user=request.user if request.user.is_authenticated else None,
        full_name=form.cleaned_data["full_name"],
        phone=form.cleaned_data["phone"],
        email=form.cleaned_data["email"],
        position=form.cleaned_data["position"],
        proof_file=form.cleaned_data.get("proof_file"),
        comment=form.cleaned_data.get("comment", ""),
        request_ip=(ip.split(",")[0].strip() if ip else None),
    )

    ActivityLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        action="ownership_claim_submitted",
        company=company,
        details=f"Ownership claim #{claim.id} by {claim.full_name} <{claim.email}>",
    )

    # Fire-and-forget Telegram notification
    try:
        send_ownership_claim_notification(claim)
    except Exception as e:
        logger.warning("Telegram ownership claim notification failed: %s", e)

    return JsonResponse({
        "ok": True,
        "message": "So'rovingiz qabul qilindi! Moderator 1-3 ish kuni ichida ko'rib chiqadi."
    })


def admin_approve_claim(request, claim_id: int):
    """Admin-only: approve an ownership claim."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)

    claim = get_object_or_404(BusinessOwnershipClaim, pk=claim_id)
    if claim.status != "pending":
        return JsonResponse({"ok": False, "error": f"Already {claim.status}"}, status=400)

    claim.status = "approved"
    claim.reviewed_at = now()
    claim.reviewed_by = request.user
    claim.save(update_fields=["status", "reviewed_at", "reviewed_by"])

    # Update company ownership
    company = claim.company
    company.is_claimed = True
    company.is_verified = True
    company.owner = claim.user
    if claim.user and not company.manager:
        company.manager = claim.user
    company.save(update_fields=["is_claimed", "is_verified", "owner", "manager"])

    ActivityLog.objects.create(
        actor=request.user,
        action="ownership_claim_approved",
        company=company,
        details=f"Claim #{claim.id} approved for {claim.full_name}",
    )

    # Edit Telegram message to show result
    try:
        from django.conf import settings as ds
        token = getattr(ds, "TELEGRAM_BOT_TOKEN", "")
        if token and claim.telegram_message_id and claim.telegram_chat_id:
            edit_telegram_message(
                chat_id=claim.telegram_chat_id,
                message_id=int(claim.telegram_message_id),
                new_text=f"✅ <b>Tasdiqlandi</b>: {company.name} → {claim.full_name}\n🆔 So'rov #{claim.id}",
                token=token,
            )
    except Exception as e:
        logger.warning("Telegram edit failed on approve: %s", e)

    # Email notification to applicant
    try:
        send_mail(
            subject="✅ Fikrly: Biznes egallash so'rovingiz tasdiqlandi",
            message=(
                f"Salom {claim.full_name},\n\n"
                f"'{company.name}' biznesini egallash so'rovingiz tasdiqlandi.\n"
                "Endi biznesingizni Fikrly'da boshqarishingiz mumkin.\n\n"
                "Rahmat!\nFikrly jamoasi"
            ),
            from_email=None,
            recipient_list=[claim.email],
            fail_silently=True,
        )
    except Exception:
        pass

    return JsonResponse({"ok": True, "status": "approved"})


def admin_reject_claim(request, claim_id: int):
    """Admin-only: reject an ownership claim."""
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)

    claim = get_object_or_404(BusinessOwnershipClaim, pk=claim_id)
    if claim.status != "pending":
        return JsonResponse({"ok": False, "error": f"Already {claim.status}"}, status=400)

    reason = request.POST.get("reason", "") or (
        json.loads(request.body).get("reason", "") if request.content_type == "application/json" else ""
    )

    claim.status = "rejected"
    claim.rejection_reason = reason
    claim.reviewed_at = now()
    claim.reviewed_by = request.user
    claim.save(update_fields=["status", "rejection_reason", "reviewed_at", "reviewed_by"])

    ActivityLog.objects.create(
        actor=request.user,
        action="ownership_claim_rejected",
        company=claim.company,
        details=f"Claim #{claim.id} rejected. Reason: {reason}",
    )

    try:
        from django.conf import settings as ds
        token = getattr(ds, "TELEGRAM_BOT_TOKEN", "")
        if token and claim.telegram_message_id and claim.telegram_chat_id:
            edit_telegram_message(
                chat_id=claim.telegram_chat_id,
                message_id=int(claim.telegram_message_id),
                new_text=f"❌ <b>Rad etildi</b>: {claim.company.name} → {claim.full_name}\nSabab: {reason or '—'}\n🆔 So'rov #{claim.id}",
                token=token,
            )
    except Exception as e:
        logger.warning("Telegram edit failed on reject: %s", e)

    # Email notification to applicant
    try:
        send_mail(
            subject="❌ Fikrly: Biznes egallash so'rovingiz rad etildi",
            message=(
                f"Salom {claim.full_name},\n\n"
                f"Afsuski, '{claim.company.name}' biznesini egallash so'rovingiz rad etildi.\n"
                f"Sabab: {reason or 'Ko\'rsatilmagan'}\n\n"
                "Savollaringiz bo'lsa, support@fikrly.uz ga murojaat qiling.\n\n"
                "Hurmat bilan,\nFikrly jamoasi"
            ),
            from_email=None,
            recipient_list=[claim.email],
            fail_silently=True,
        )
    except Exception:
        pass

    return JsonResponse({"ok": True, "status": "rejected"})


@csrf_exempt
@ratelimit(key="ip", rate="30/m", method="POST", block=False)
def telegram_claim_webhook(request):
    """Webhook called by Telegram bot for inline button callbacks (approve/reject)."""
    import json as _json
    from django.conf import settings as ds

    # Validate secret token header
    secret = request.META.get("HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN", "")
    expected = getattr(ds, "TELEGRAM_WEBHOOK_SECRET", "")
    if expected and secret != expected:
        return JsonResponse({"ok": False}, status=403)

    try:
        body = _json.loads(request.body)
    except Exception:
        return JsonResponse({"ok": False}, status=400)

    callback_query = body.get("callback_query")
    if not callback_query:
        return JsonResponse({"ok": True})  # ignore non-callback updates

    callback_id = callback_query.get("id", "")
    data = callback_query.get("data", "")
    token = getattr(ds, "TELEGRAM_BOT_TOKEN", "")

    if ":" not in data:
        answer_telegram_callback(callback_id, "❓ Noma'lum buyruq", token)
        return JsonResponse({"ok": True})

    action, _, claim_id_str = data.partition(":")
    try:
        claim_id = int(claim_id_str)
    except ValueError:
        answer_telegram_callback(callback_id, "❓ Noma'lum ID", token)
        return JsonResponse({"ok": True})

    try:
        claim = BusinessOwnershipClaim.objects.select_related("company", "user").get(pk=claim_id)
    except BusinessOwnershipClaim.DoesNotExist:
        answer_telegram_callback(callback_id, "❓ So'rov topilmadi", token)
        return JsonResponse({"ok": True})

    if claim.status != "pending":
        answer_telegram_callback(callback_id, f"ℹ️ Allaqon: {claim.get_status_display()}", token)
        return JsonResponse({"ok": True})

    if action == "claim_approve":
        claim.status = "approved"
        claim.reviewed_at = now()
        claim.save(update_fields=["status", "reviewed_at"])
        company = claim.company
        company.is_claimed = True
        company.is_verified = True
        company.owner = claim.user
        if claim.user and not company.manager:
            company.manager = claim.user
        company.save(update_fields=["is_claimed", "is_verified", "owner", "manager"])

        answer_telegram_callback(callback_id, f"✅ Tasdiqlandi: {company.name}", token)
        try:
            msg_id = int(claim.telegram_message_id) if claim.telegram_message_id else None
            if msg_id and claim.telegram_chat_id:
                edit_telegram_message(
                    chat_id=claim.telegram_chat_id,
                    message_id=msg_id,
                    new_text=f"✅ <b>TASDIQLANDI</b>\n\n🏢 {company.name}\n👤 {claim.full_name}\n🆔 So'rov #{claim.id}",
                    token=token,
                )
        except Exception:
            pass
        # Notify claimant
        try:
            send_mail(
                subject="✅ Fikrly: Biznes egallash so'rovingiz tasdiqlandi",
                message=(
                    f"Salom {claim.full_name},\n\n"
                    f"'{company.name}' biznesini egallash so'rovingiz tasdiqlandi.\n\n"
                    "Rahmat!\nFikrly jamoasi"
                ),
                from_email=None,
                recipient_list=[claim.email],
                fail_silently=True,
            )
        except Exception:
            pass

    elif action == "claim_reject":
        claim.status = "rejected"
        claim.reviewed_at = now()
        claim.save(update_fields=["status", "reviewed_at"])
        answer_telegram_callback(callback_id, f"❌ Rad etildi: {claim.company.name}", token)
        try:
            msg_id = int(claim.telegram_message_id) if claim.telegram_message_id else None
            if msg_id and claim.telegram_chat_id:
                edit_telegram_message(
                    chat_id=claim.telegram_chat_id,
                    message_id=msg_id,
                    new_text=f"❌ <b>RAD ETILDI</b>\n\n🏢 {claim.company.name}\n👤 {claim.full_name}\n🆔 So'rov #{claim.id}",
                    token=token,
                )
        except Exception:
            pass
        try:
            send_mail(
                subject="❌ Fikrly: Biznes egallash so'rovingiz rad etildi",
                message=(
                    f"Salom {claim.full_name},\n\n"
                    f"Afsuski, '{claim.company.name}' biznesini egallash so'rovingiz rad etildi.\n\n"
                    "Savollaringiz bo'lsa, support@fikrly.uz ga murojaat qiling.\n\n"
                    "Hurmat bilan,\nFikrly jamoasi"
                ),
                from_email=None,
                recipient_list=[claim.email],
                fail_silently=True,
            )
        except Exception:
            pass
    else:
        answer_telegram_callback(callback_id, "❓ Noma'lum harakat", token)

    return JsonResponse({"ok": True})


def company_detail(request, pk: int):
    company = get_object_or_404(
        Company.objects.select_related("category_fk"),
        pk=pk,
    )
    if not is_company_publicly_visible(company) and not (
        request.user.is_superuser
        or (request.user.is_authenticated and company.manager == request.user)
    ):
        raise Http404

    session_key = f"viewed_company_{pk}"
    if not request.session.get(session_key):
        Company.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
        request.session[session_key] = True

    company.assessment = compute_assessment(float(company.rating), int(company.review_count))
    base_reviews_qs = company.reviews.filter(is_approved=True)
    reviews_qs = base_reviews_qs

    sort = request.GET.get("sort", "most_liked")
    with_text = request.GET.get("with_text") in ("1", "true", "on")
    with_response = request.GET.get("with_response") in ("1", "true", "on")
    stars_list = request.GET.getlist("stars")
    if len(stars_list) == 1 and "," in stars_list[0]:
        stars_list = [s.strip() for s in stars_list[0].split(",") if s.strip()]
    try:
        stars_selected = sorted(
            {int(s) for s in stars_list if str(s).isdigit() and 1 <= int(s) <= 5},
            reverse=True,
        )
    except Exception:
        stars_selected = []

    if with_text:
        reviews_qs = reviews_qs.filter(~Q(text=""))
    if stars_selected:
        reviews_qs = reviews_qs.filter(rating__in=stars_selected)
    if with_response:
        reviews_qs = reviews_qs.exclude(owner_response_text="")

    if sort == "highest":
        reviews_qs = reviews_qs.order_by("-rating", "-created_at")
    elif sort == "lowest":
        reviews_qs = reviews_qs.order_by("rating", "-created_at")
    elif sort == "newest":
        reviews_qs = reviews_qs.order_by("-created_at")
    else:
        reviews_qs = reviews_qs.order_by("-like_count", "-created_at")

    dist_counts = {i: 0 for i in range(1, 6)}
    agg = base_reviews_qs.values("rating").annotate(c=Count("id"))
    for row in agg:
        r = int(row["rating"])
        if 1 <= r <= 5:
            dist_counts[r] = int(row["c"])
    total = sum(dist_counts.values()) or 1
    dist = [
        {"star": star, "count": dist_counts.get(star, 0), "percent": round((dist_counts.get(star, 0) / total) * 100)}
        for star in range(5, 0, -1)
    ]

    reviews_qs = reviews_qs.select_related("user").prefetch_related("likes")
    paginator = Paginator(reviews_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    qd = request.GET.copy()
    qd.pop("page", None)
    qs_base = qd.urlencode()
    if qs_base:
        qs_base = qs_base + "&"

    qd_no_stars = request.GET.copy()
    for k in ["page", "stars"]:
        qd_no_stars.pop(k, None)
    qs_no_stars = qd_no_stars.urlencode()
    if qs_no_stars:
        qs_no_stars = qs_no_stars + "&"

    reviews = page_obj

    if request.user.is_authenticated:
        from ..models import ReviewLike
        user_likes = set(
            ReviewLike.objects.filter(user=request.user, review__in=reviews)
            .values_list("review_id", flat=True)
        )
        for r in reviews:
            r.is_liked_by_user = r.id in user_likes

    current = page_obj.number
    total_pages = paginator.num_pages
    similar_companies = (
        public_companies_queryset()
        .filter(category_fk=company.category_fk)
        .exclude(pk=company.pk)
        .order_by("-rating", "-review_count")[:3]
    )

    window = 2
    start = max(1, current - window)
    end = min(total_pages, current + window)
    pages_to_show = list(range(start, end + 1))

    filters_active = bool(with_text or with_response or stars_selected)
    qd_clear = request.GET.copy()
    for k in ["with_text", "with_response", "stars", "page"]:
        qd_clear.pop(k, None)
    clear_filters_qs = qd_clear.urlencode()

    years_on_site = max(0, int((timezone.now() - company.created_at).days // 365))
    if company.lat and company.lng:
        map_url = f"https://www.google.com/maps/search/?api=1&query={company.lat},{company.lng}"
    elif company.address:
        from urllib.parse import quote
        q = quote(f"{company.address} {company.city}")
        map_url = f"https://www.google.com/maps/search/?api=1&query={q}"
    else:
        map_url = ""

    liked_state = False
    if request.user.is_authenticated:
        liked_state = CompanyLike.objects.filter(company=company, user=request.user).exists()

    # Ownership claim context
    pending_ownership_claim = BusinessOwnershipClaim.objects.filter(
        company=company, status="pending"
    ).first()
    user_has_pending_claim = False
    if request.user.is_authenticated and pending_ownership_claim:
        user_has_pending_claim = (pending_ownership_claim.user == request.user)

    return render(
        request,
        "pages/company_detail.html",
        {
            "company": company,
            "reviews": reviews,
            "rating_distribution": dist,
            "page_obj": page_obj,
            "paginator": paginator,
            "current_sort": sort,
            "with_text": with_text,
            "with_response": with_response,
            "current_stars": stars_selected,
            "qs_base": qs_base,
            "star_options": [5, 4, 3, 2, 1],
            "qs_no_stars": qs_no_stars,
            "pages_to_show": pages_to_show,
            "filters_active": filters_active,
            "clear_filters_qs": clear_filters_qs,
            "years_on_site": years_on_site,
            "map_url": map_url,
            "liked_state": liked_state,
            "similar_companies": similar_companies,
            "canonical_url": request.build_absolute_uri(),
            "pending_ownership_claim": pending_ownership_claim,
            "user_has_pending_claim": user_has_pending_claim,
        },
    )


@login_required
@ratelimit(key="user", rate="10/m", method="POST")
def reveal_contact(request, pk: int, kind: str):
    """Reveal phone or email; increments counters and logs activity."""
    try:
        company = Company.objects.select_related("category_fk").get(pk=pk)
        if not is_company_publicly_visible(company) and not (
            request.user.is_superuser
            or (request.user.is_authenticated and company.manager == request.user)
        ):
            raise Http404
    except Company.DoesNotExist:
        raise Http404

    if kind not in ("phone", "email"):
        return JsonResponse({"ok": False, "error": "invalid"}, status=400)
    value = company.phone_public if kind == "phone" else company.email_public
    if not value:
        return JsonResponse({"ok": False, "error": "not_set"}, status=404)
    ActivityLog.objects.create(
        actor=request.user, action="contact_revealed", company=company,
        details=f"{kind} revealed",
    )
    return JsonResponse({"ok": True, "value": value})


@login_required
@ratelimit(key="user", rate="20/m", method="POST")
def like_company(request, pk: int):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "POST required"}, status=405)

    try:
        company = Company.objects.select_related("category_fk").get(pk=pk)
        if not is_company_publicly_visible(company) and not (
            request.user.is_superuser
            or (request.user.is_authenticated and company.manager == request.user)
        ):
            raise Http404
    except Company.DoesNotExist:
        raise Http404

    liked = False
    obj, created = CompanyLike.objects.get_or_create(company=company, user=request.user)
    if created:
        liked = True
        Company.objects.filter(pk=pk).update(like_count=F("like_count") + 1)
        ActivityLog.objects.create(
            actor=request.user, action="company_liked", company=company, details="liked"
        )
    else:
        obj.delete()
        Company.objects.filter(pk=pk, like_count__gt=0).update(like_count=F("like_count") - 1)
        ActivityLog.objects.create(
            actor=request.user, action="company_liked", company=company, details="unliked"
        )

    current = Company.objects.filter(pk=pk).values_list("like_count", flat=True).first()
    return JsonResponse({"ok": True, "like_count": int(current or 0), "liked": liked})


@xframe_options_exempt
def company_widget(request, pk):
    """Embeddable trust badge iframe for third-party sites.

    GET params
    ----------
    theme : ``light`` (default) | ``dark`` | ``auto``
    size  : ``sm`` | ``md`` (default) | ``lg``
    style : ``full`` (default) | ``compact``
    """
    VALID_THEMES = {"light", "dark", "auto"}
    VALID_SIZES  = {"sm", "md", "lg"}
    VALID_STYLES = {"full", "compact"}

    theme = request.GET.get("theme", "light")
    size  = request.GET.get("size",  "md")
    style = request.GET.get("style", "full")

    # Sanitise – fall back to defaults on invalid / missing input (no 400, no crash)
    if theme not in VALID_THEMES: theme = "light"
    if size  not in VALID_SIZES:  size  = "md"
    if style not in VALID_STYLES: style = "full"

    company  = get_object_or_404(Company, pk=pk, is_active=True)
    base_url = f"{request.scheme}://{request.get_host()}"

    response = render(request, "pages/company_widget.html", {
        "company":  company,
        "theme":    theme,
        "size":     size,
        "style":    style,
        "base_url": base_url,
    })
    # ── Cache (each param combo = unique URL, no Vary needed) ──
    response["Cache-Control"] = "public, max-age=300"
    # ── Security headers ──
    # Widget will be embedded in third-party iframes so we relax frame-ancestors
    # but lock down everything else.
    response["Content-Security-Policy"] = (
        "default-src 'none'; "
        "style-src 'unsafe-inline'; "
        "img-src https: data:; "
        "font-src 'none'; "
        "script-src 'none'; "
        "frame-ancestors *;"
    )
    # Allow cross-origin embedding while sending referrer for the backlink
    response["Referrer-Policy"] = "no-referrer-when-downgrade"
    response["X-Content-Type-Options"] = "nosniff"
    return response
