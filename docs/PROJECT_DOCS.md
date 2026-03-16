# Fikrly Platform — Complete Project Documentation

**Last updated:** 2026-03-11  
**Django:** 5.2.4 · **Python:** 3.12 · **DB:** PostgreSQL 15 · **Cache:** Redis 7  
**Live:** https://fikrly.uz  

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Directory Structure](#3-directory-structure)
4. [Data Models](#4-data-models)
5. [URL Routes](#5-url-routes)
6. [Views](#6-views)
7. [Forms](#7-forms)
8. [Middleware](#8-middleware)
9. [Signals](#9-signals)
10. [Admin Panel](#10-admin-panel)
11. [Templates](#11-templates)
12. [Static Files & Assets](#12-static-files--assets)
13. [i18n / Localisation](#13-i18n--localisation)
14. [Authentication & Accounts](#14-authentication--accounts)
15. [Notifications (Email + Telegram)](#15-notifications-email--telegram)
16. [Caching Strategy](#16-caching-strategy)
17. [Analytics (GA4 + GTM)](#17-analytics-ga4--gtm)
18. [Management Commands](#18-management-commands)
19. [Docker & Infrastructure](#19-docker--infrastructure)
20. [Settings Reference](#20-settings-reference)
21. [Environment Variables](#21-environment-variables)
22. [Testing](#22-testing)
23. [Deployment Runbook](#23-deployment-runbook)
24. [Known Issues & TODOs](#24-known-issues--todos)

---

## 1. Project Overview

**Fikrly** is an Uzbek-language business review platform — the "Trustpilot of Uzbekistan". Users can:
- Browse and search companies by category and city
- Leave reviews (1–5 stars) with optional receipt photos
- Like companies and mark reviews as helpful
- Claim ownership of their business listing
- Business managers can respond to reviews and edit their profile

The platform is bilingual: **Uzbek** (default) and **Russian** (prefix `/ru/`).

---

## 2. Architecture

```
Browser
  │
  ▼
nginx:443/80  (TLS termination, static/media file serving)
  │
  ▼
gunicorn:8000  (4 workers × 2 threads)
  │
  ├─── Django 5.2.4 app (myproject/wsgi.py)
  │       ├─ frontend app  (all business logic)
  │       ├─ core app      (custom 404/500, context processors)
  │       └─ django-allauth (auth, Google OAuth)
  │
  ├─── PostgreSQL 15  (primary data store)
  └─── Redis 7        (page cache, session, rate-limit counters)
```

**Request lifecycle:**
1. nginx receives HTTPS request, terminates TLS
2. Proxies to gunicorn on `fikrly_web:8000`
3. Django middleware stack processes the request (security, locale, CSP, no-cache headers)
4. URL router dispatches to a view function
5. View queries PostgreSQL (via Django ORM), checks Redis cache
6. Template rendered with context, response returned

---

## 3. Directory Structure

```
/home/maymun/fikrly/
├── manage.py                   # Django management entry point
├── Makefile                    # Docker shortcuts (make build, make up, etc.)
├── Dockerfile                  # Multi-stage Python 3.12 image
├── docker-compose.yml          # web + nginx + db + redis
├── requirements.txt            # Core Python deps
├── requirements-prod.txt       # Production-only extras
├── .env                        # Local env vars (not committed)
├── .venv/                      # Local virtual environment
│
├── myproject/                  # Django project package
│   ├── settings.py             # All configuration
│   ├── urls.py                 # Root URL conf
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point (unused)
│
├── frontend/                   # Main Django app
│   ├── models.py               # All DB models (898 lines)
│   ├── urls.py                 # App-level URL conf (221 lines)
│   ├── admin.py                # Admin panel customisation (1 049 lines)
│   ├── forms.py                # All Django forms
│   ├── signals.py              # Signal handlers (419 lines)
│   ├── middleware.py           # Custom middleware (188 lines)
│   ├── views/                  # View modules
│   │   ├── __init__.py         # Re-exports all views
│   │   ├── company.py          # Company, home, dashboard views (1 254 lines)
│   │   ├── review.py           # Review CRUD + votes (358 lines)
│   │   ├── profile.py          # User & public profile (94 lines)
│   │   └── misc.py             # Static pages, language switch, utils (286 lines)
│   ├── advanced_views.py       # Gamification, exports, advanced features
│   ├── moderation_views.py     # Admin moderation + Telegram webhook
│   ├── visibility.py           # Public queryset helpers
│   ├── cache_utils.py          # Cache decorators and helpers
│   ├── utils.py                # Telegram notifications, Wilson score
│   ├── email_notifications.py  # Email notification service
│   ├── image_optimization.py   # WebP image generation
│   ├── sitemaps.py             # XML sitemaps (company, category, static)
│   ├── adapters.py             # django-allauth account/social adapters
│   ├── allauth_forms.py        # Custom signup form
│   ├── translation.py          # django-modeltranslation field registration
│   ├── apps.py                 # AppConfig
│   ├── migrations/             # 51 DB migration files
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Master layout (GTM, GA, nav, footer)
│   │   ├── pages/              # 23 page templates
│   │   └── errors/             # 404, 500 templates
│   ├── static/                 # App-level static files
│   ├── templatetags/           # Custom template tags
│   ├── management/commands/    # 14 custom management commands
│   └── tests/                  # Test suite
│
├── core/                       # Minimal helper app
│   ├── context_processors.py   # Injects GA_MEASUREMENT_ID + GTM_ID
│   └── views.py                # Custom 404/500 handlers
│
├── locale/                     # Translation .po/.mo files (uz, ru)
├── staticfiles/                # Collected static (generated, not committed)
├── media/                      # User-uploaded files
├── logs/                       # Rotating log files
├── nginx/                      # Nginx config (host)
├── deploy/                     # Server deployment scripts
├── docker/                     # Docker helper scripts
├── scripts/                    # One-off data scripts
└── tests/                      # E2E / integration tests (Playwright)
```

---

## 4. Data Models

All models live in `frontend/models.py`.

### BusinessCategory
Taxonomy for grouping companies.

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField(100)` | Unique, translated (uz/ru) |
| `slug` | `SlugField(100)` | URL-friendly, unique |
| `icon_svg` | `TextField` | Inline SVG path content |
| `color` | `CharField(20)` | `red/orange/yellow/green/blue/purple/pink/gray` |
| `is_featured` | `BooleanField` | Show on homepage |
| `is_active` | `BooleanField` | Hides category + all its companies when False |

**Key property:** `display_name` — returns Russian translation when `lang == 'ru'`.

---

### Company
Central entity. Represents a business listing.

| Field | Type | Notes |
|---|---|---|
| `name` | `CharField(255)` | Unique |
| `slug` | `SlugField(280)` | Unique, auto-generated from name, used in canonical URL |
| `category_fk` | `FK → BusinessCategory` | `SET_NULL` on delete |
| `city` | `CharField(100)` | Optional |
| `description` | `TextField` | Translated (uz/ru) |
| `image` | `ImageField` | Original upload |
| `image_400/800/1200` | `ImageField` | Auto-generated WebP variants |
| `logo` | `ImageField` | Via `company_logo_path()` using UUID filename |
| `logo_url` | `URLField` | External logo fallback |
| `logo_url_backup` | `URLField` | Auto-saved from `logo_url`, editable=False |
| `logo_scale` | `PositiveIntegerField` | CSS scale % (default 100) |
| `website` | `URLField` | External website |
| `official_email_domain` | `CharField(100)` | For claim verification |
| `tax_id` | `CharField(32)` | INN/СТИР (optional) |
| `address` | `CharField(255)` | |
| `landmark` | `CharField(255)` | Near landmark hint |
| `phone_public` | `CharField(60)` | |
| `email_public` | `EmailField` | |
| `facebook_url` / `telegram_url` / `instagram_url` | `URLField` | Social links |
| `lat` / `lng` | `DecimalField` | Map coordinates |
| `working_hours` | `JSONField` | Weekly schedule |
| `library_image_path` | `CharField(255)` | Points into `media/company_library/` |
| `manager` | `FK → User` | Company manager (internal role) |
| `is_verified` | `BooleanField` | Admin-verified badge |
| `verification_document` | `FileField` | Verification proof |
| `is_active` | `BooleanField` | Soft-delete / hide from public |
| `is_claimed` | `BooleanField` | Ownership claim confirmed |
| `owner` | `FK → User` | Verified business owner |
| `rating` | `DecimalField(3,2)` | Denormalised average, updated on review save |
| `review_count` | `PositiveIntegerField` | Denormalised count |
| `like_count` | `PositiveIntegerField` | Denormalised total likes |
| `view_count` | `PositiveIntegerField` | Incremented on detail page visits |

**DB indexes:** `(is_active, -rating)`, `(is_active, -review_count)`, `(category_fk, is_active, -rating)`, `(city, is_active)`, `(is_verified, is_active)`.

**Key methods:**
- `save()` — auto-generates WebP variants via `image_optimization.py` when `image` changes
- `display_logo` — priority: uploaded file → `logo_url` → `logo_url_backup`
- `display_image_url` — uploaded image → library path → `image_url`
- `display_description` — returns Russian when active language is `ru`
- `image_url_for_size(size)` — returns URL for 400/800/1200 WebP variant

---

### Review
User-submitted company review.

| Field | Type | Notes |
|---|---|---|
| `company` | `FK → Company` | `CASCADE` |
| `user` | `FK → User` | Nullable (`SET_NULL`) — anonymous allowed |
| `user_name` | `CharField(120)` | Display name (filled from user on submit) |
| `rating` | `PositiveSmallIntegerField` | 1–5 |
| `text` | `TextField` | Body |
| `receipt` | `ImageField` | Optional purchase proof (max 5 MB) |
| `is_approved` | `BooleanField` | Shown publicly only when True |
| `approval_requested` | `BooleanField` | Set True on submit |
| `owner_response_text` | `TextField` | Manager reply |
| `owner_response_at` | `DateTimeField` | When manager replied |
| `like_count` | `PositiveIntegerField` | Denormalised |
| `helpful_count` | `PositiveIntegerField` | Denormalised |
| `not_helpful_count` | `PositiveIntegerField` | Denormalised |

**Constraint:** `unique_review_per_user_per_company` — one review per authenticated user per company (NULL users excluded).

**Moderation flow:** `is_approved=False` on create → Telegram notification → admin approves in panel → `is_approved=True` → visible publicly.

---

### ReviewLike
Per-user like for a review. `unique_together = (review, user)`.

### CompanyLike
Per-user like for a company. `unique_together = (company, user)`.

### ReviewReport
Abuse report on a review. Reasons: `spam / abuse / false / pii / other`. Statuses: `open / resolved / rejected`.

### ReviewHelpfulVote
`helpful` or `not_helpful` vote per user per review. `unique_together = (review, user)`.

### ReviewImage
Image attachment on a review (optional, for future use).

### UserProfile
One-to-one extension of `auth.User`.

| Field | Notes |
|---|---|
| `avatar` | `ImageField` |
| `bio` | `TextField` |
| `is_approved` | Admin approval gate (auto-approved on allauth signup) |
| `requested_approval_at` / `approved_at` | Timestamps |
| `username_change_log` | `JSONField` — tracks change history (limit: 2 per 3 days) |

### ActivityLog
Audit trail of actions. Actions: `company_edit`, `approval_requested`, `review_approved`, `owner_responded`, `review_created`, `review_reported`, `company_claim_requested`, `company_claim_verified`, `contact_revealed`, `company_liked`.

### CompanyClaim
Email-token-based lightweight ownership claim. Statuses: `pending / verified / rejected / expired`. Token: 64-char unique, indexed. Expires set on creation.

### BusinessOwnershipClaim
Full ownership claim with document proof for admin moderation. Positions: `owner / manager / other`. Statuses: `pending / approved / rejected`. Includes `full_name`, `phone`, `email`, `proof` file.

### UserGamification
Points and level tracking per user. Links to `Badge` records.

### Badge
Achievement badge earned by a user. Has `earned_at` timestamp.

### DataExport
Tracks export requests (admin-generated reports).

### ReviewFlag
Internal flag on a review for moderation queue.

---

## 5. URL Routes

### Root URL conf (`myproject/urls.py`)
| Pattern | View | Name |
|---|---|---|
| `i18n/setlang/` | `safe_set_language` | `set_language` |
| `robots.txt` | `robots_txt` | `robots_txt` |
| `sitemap.xml` | Django sitemap view | `sitemap` |
| `favicon.ico` | `favicon_file` | `favicon` |
| `service-worker.js` | `service_worker` | `service_worker` |
| `BingSiteAuth.xml` | `bing_site_auth` | `bing_site_auth` |
| `api/tg/webhook/` | `telegram_webhook` | `telegram_webhook` |
| `admin/` | Django admin | — |
| `accounts/` | django-allauth | — |

*(All app routes are prefixed by `i18n_patterns` — `/ru/` prefix for Russian, none for Uzbek.)*

### App URL conf (`frontend/urls.py`) — key routes
| Pattern | View | Name |
|---|---|---|
| `` (empty) | `home` | `index` |
| `profile/` | `user_profile` | `user_profile` |
| `users/<username>/` | `public_profile` | `public_profile` |
| `bizneslar/` | `business_list` | `business_list` |
| `kategoriyalar/` | `category_browse` | `category_browse` |
| `kategoriyalar/<slug>/` | `business_list` | `business_list_by_category` |
| `sharh-yozish/` | `review_submission` | `review_submission` |
| `bizneslar/<slug:slug>/` | `company_detail` | `company_detail` |
| `bizneslar/<int:pk>/` | `company_detail_by_pk` | — (301 → slug URL) |
| `widget/<pk>/` | `company_widget` | `company_widget` |
| `business-dashboard/` | `business_dashboard` | `business_dashboard` |
| `manager/company/<pk>/edit/` | `manager_company_edit` | `manager_company_edit` |
| `manager/reviews/<pk>/respond/` | `manager_review_response` | `manager_review_response` |
| `reviews/<pk>/like/` | `like_review` | `like_review` |
| `business/<pk>/like/` | `like_company` | `like_company` |
| `api/reviews/<pk>/vote/` | `vote_review_helpful` | `vote_review_helpful` |
| `api/search-suggestions/` | `search_suggestions_api` | `search_suggestions_api` |
| `business/<pk>/claim/` | `claim_company` | `claim_company` |
| `claim/verify/<token>/` | `verify_claim` | `verify_claim` |
| `business/<pk>/reveal/<kind>/` | `reveal_contact` | `reveal_contact` |
| `privacy-policy/` | `privacy_policy` | `privacy_policy` |
| `terms/` | `terms_of_service` | `terms_of_service` |
| `community-guidelines/` | `community_guidelines` | `community_guidelines` |
| `contact/` | `contact_us` | `contact_us` |
| `widgets/` | `widgets_page` | `widgets_page` |

Older paths (`business-list/`, `category-browse/`, `review-submission/`, `business/<pk>/`, `biziness/<pk>/`, `biznes/<pk>/`) redirect **301** to canonical URLs.

`health/` is registered outside `i18n_patterns` (direct HTTP, no language prefix) for Docker healthcheck compatibility.

---

## 6. Views

### `frontend/views/company.py` — 1 254 lines

| Function | Auth | Description |
|---|---|---|
| `home(request)` | public | Homepage. Top companies by rating, trending by review_count, latest approved reviews, featured categories. Anonymous GET cached 5 min per language. |
| `business_dashboard(request)` | `@login_required` | Manager dashboard: managed companies + pending reviews. |
| `business_list(request)` | public | Paginated company listing. Supports search (`q`), category filter (`category`), city filter (`city`), sort (`sort`), verified filter (`verified`). Uses full-text search (PostgreSQL `TrigramSimilarity` / `SearchVector`) when available, falls back to `icontains`. |
| `company_detail(request, slug)` | public | Company profile page. Looks up by `slug` field. Reviews paginated (sorted by date/helpful). View count incremented once per session. Returns 404 for inactive companies. |
| `company_detail_by_pk(request, pk)` | public | 301 redirect from legacy `bizneslar/<pk>/` to canonical `bizneslar/<slug>/`. |
| `manager_company_edit(request, pk)` | `@login_required` | Company manager edits their listing. Diffs fields and logs to `ActivityLog`. |
| `manager_request_approval(request, pk)` | `@login_required` | Manager requests admin approval for a review response. |
| `manager_review_response(request, pk)` | `@login_required` | Manager posts a response to a user review. |
| `claim_company(request, pk)` | `@login_required` | Lightweight email-token claim flow. Sends verification email. |
| `verify_claim(request, token)` | public | Verifies claim by token. Marks company `is_claimed=True`, sets `owner`. |
| `submit_ownership_claim(request, pk)` | `@login_required` | Full ownership claim with document upload. |
| `admin_approve_claim(request, pk)` | `@staff_required` | Admin approves ownership claim. |
| `admin_reject_claim(request, pk)` | `@staff_required` | Admin rejects ownership claim. |
| `like_company(request, pk)` | `@login_required` | Toggle company like. Returns JSON `{liked, count}`. |
| `like_review(request, pk)` | `@login_required` | Toggle review like. Returns JSON `{liked, count}`. |
| `vote_review_helpful(request, pk)` | `@login_required` | Submit helpful/not-helpful vote. Returns JSON. |
| `reveal_contact(request, pk, kind)` | `@login_required` | Reveal phone/email, logs `ActivityLog`. |
| `search_suggestions_api(request)` | public | Autocomplete search suggestions JSON endpoint. |
| `company_widget(request, pk)` | public | Embeddable company rating widget (`@xframe_options_exempt`). |
| `verification_badge(request, pk)` | public | Embeddable verification badge. |

### `frontend/views/review.py` — 358 lines

| Function | Auth | Description |
|---|---|---|
| `review_submission(request)` | `@login_required` | Create review. Validates 1–5 rating, checks one-review-per-company constraint, custom rate limit (15/5 min via Redis). Sends email notification after save. |
| `review_edit(request, pk)` | `@login_required` | Edit own review (owner check). |
| `review_delete(request, pk)` | `@login_required` | Delete own review (owner check). Updates company `rating`/`review_count` aggregates. |
| `report_review(request, pk)` | `@login_required` | Submit abuse report on a review. Rate-limited. |

### `frontend/views/profile.py` — 94 lines

| Function | Auth | Description |
|---|---|---|
| `user_profile(request)` | `@login_required` | Edit profile (avatar, bio, username, name). Shows own reviews, stats, gamification badges. |
| `public_profile(request, username)` | public | Read-only public profile with approved reviews and stats. |

### `frontend/views/misc.py` — 286 lines

| Function | Notes |
|---|---|
| `safe_set_language(request)` | Language switcher. Validates `next` URL against `allowed_hosts` (SSRF-safe). Rewrites `/ru/` prefix. |
| `robots_txt(request)` | Serves `robots.txt` |
| `favicon_file(request)` | Serves `favicon.ico` |
| `service_worker(request)` | Serves PWA service worker JS |
| `bing_site_auth(request)` | Serves Bing webmaster XML |
| `privacy_policy` / `terms_of_service` / `community_guidelines` / `contact_us` / `widgets_page` | Static content pages |

### `frontend/moderation_views.py`
- `telegram_webhook(request)` — receives Telegram callback queries (approve/reject review buttons). Validates `X-Telegram-Bot-Api-Secret-Token` header. Applies moderation action and answers the callback.
- `moderation_dashboard(request)` — admin-only moderation list page.

---

## 7. Forms

| Form | Model | Key fields |
|---|---|---|
| `ReviewForm` | `Review` | `company`, `user_name`, `rating`, `text`, `receipt`. Validates receipt ≤ 5 MB. Queryset filtered to `public_companies_queryset()`. |
| `ProfileForm` | `UserProfile` | `avatar`, `bio` + `username`, `first_name`, `last_name` (on User). Username change limited to 2× per 3 days via `username_change_log`. |
| `CompanyManagerEditForm` | `Company` | Manager-editable fields only. |
| `ReviewEditForm` | `Review` | `rating`, `text` only. |
| `ReportReviewForm` | `ReviewReport` | `reason`, `details`. |
| `OwnerResponseForm` | `Review` | `owner_response_text`. |
| `ClaimCompanyForm` | `CompanyClaim` | `email`. |
| `BusinessOwnershipClaimForm` | `BusinessOwnershipClaim` | Full claim with document. |
| `ContactForm` | (not a model form) | Name, email, message. Sends email + Telegram. |
| `CustomSignupForm` | `auth.User` (allauth) | Extended signup. |

---

## 8. Middleware

Order in `settings.py → MIDDLEWARE`:

| Middleware | Purpose |
|---|---|
| `SecurityMiddleware` | Security headers (Django built-in) |
| `WhiteNoiseMiddleware` | Serve compressed static files from `staticfiles/` |
| `SessionMiddleware` | Session handling |
| `UzbekDefaultLocaleMiddleware` | Custom locale: URL-prefix-based language activation, ignores `Accept-Language` header |
| `CommonMiddleware` | URL trailing-slash normalisation |
| `ContentSecurityPolicyMiddleware` | Injects `Content-Security-Policy` header |
| `NoCacheMiddleware` | Sets `no-store` on HTML/JSON responses (and all `/accounts/` pages) |
| `CsrfViewMiddleware` | CSRF protection |
| `AuthenticationMiddleware` | User binding to request |
| `AccountMiddleware` | django-allauth |
| `PostLoginRedirectMiddleware` | Restores pre-login URL from session on successful auth |
| `MessageMiddleware` | Flash messages |
| `XFrameOptionsMiddleware` | `X-Frame-Options: DENY` |

### `UzbekDefaultLocaleMiddleware`
- Activates `ru` if path starts with `/ru/`, otherwise `uz`
- Sets `LANGUAGE_COOKIE_NAME` on every response to keep the cookie in sync
- Intentionally ignores `Accept-Language` header

### `PostLoginRedirectMiddleware`
- After authentication, reads `_next_after_login` or `post_login_redirect` from session
- Redirects once, then clears the key to prevent redirect loops

---

## 9. Signals

File: `frontend/signals.py` (419 lines).

| Signal | Sender | Handler | What it does |
|---|---|---|---|
| `post_save` | `User` | `create_profile_on_user_create` | Creates `UserProfile` on new user (skips fixtures) |
| `user_signed_up` | allauth | `handle_user_signed_up` | Auto-approves profile, preserves post-login redirect |
| `user_logged_in` | Django auth | `handle_user_logged_in` | Restores redirect intent into session |
| `post_save` | `Review` (created=True) | `notify_new_review` | Sends Telegram notification with inline Approve/Reject buttons |
| `post_save` | `Review` | Cache invalidation | Clears public page cache entries for the affected company |
| `post_delete` | `Review` | Rating recalculation | Recalculates `company.rating` and `company.review_count` |
| `post_save` | `CompanyLike` | `update_like_count` | Updates `company.like_count` denormalised field |
| `post_delete` | `CompanyLike` | `update_like_count_on_delete` | Same as above |

---

## 10. Admin Panel

File: `frontend/admin.py` (1 049 lines).

### Custom admin actions
- `clear_public_cache_action` — clears Redis public cache keys (emergency refresh)

### Registered models and key features

| Model | Key features |
|---|---|
| `CompanyAdmin` | Inline `ActivityLog`. Custom `save_model` diffs fields and writes `ActivityLog`. Filter by verified/active/category. Image preview. Bulk activate/deactivate. |
| `ReviewAdmin` | Filter by `is_approved`. Bulk approve/reject actions. Inline `ReviewReport`. Shows receipt image preview. |
| `BusinessCategoryAdmin` | Icons preview, slug auto-generation. |
| `UserProfileAdmin` | Inline on User. Approve/unapprove actions. |
| `ActivityLogAdmin` | Read-only. Filters by action type and date. |
| `ReviewReportAdmin` | Resolve/reject actions. |
| `BusinessOwnershipClaimAdmin` | Approve/reject with Telegram notification. |
| `CompanyClaimAdmin` | Verify/expire actions. |
| `ReviewHelpfulVoteAdmin` | Read-only vote inspector. |
| `UserGamificationAdmin` | Points and level editor. |
| `BadgeAdmin` | Award badges manually. |

Custom admin site title: set in `frontend/admin_site.py`.

---

## 11. Templates

### `base.html` — master layout
- Loads: `static`, `static_bust`, `i18n`, `i18n_extras`
- `<head>`: GTM script (conditional on `GTM_ID`), meta tags, favicons, PWA manifest, CSS bundles, Google Fonts (Inter), Yandex verification, hreflang alternates, JSON-LD structured data, dark mode init script, Tailwind CDN, GA4 (conditional)
- `<body>`: GTM noscript, sticky header with search, language switcher, auth nav, mobile menu, flash messages via data attributes, main content block, footer with widget CTA, social links, sitemap navigation
- Dark mode toggle stored in `localStorage.theme`

### Page Templates (`frontend/templates/pages/`)

| Template | Route | Description |
|---|---|---|
| `home.html` | `/` | Hero, top companies grid, trending section, latest reviews strip, featured categories |
| `business_list.html` | `/bizneslar/` | Company listing with search, category/city/sort/verified filters, pagination |
| `company_detail.html` | `/bizneslar/<pk>/` | Company profile: logo, info, working hours, map, reviews list with helpful votes, owner response thread |
| `category_browse.html` | `/kategoriyalar/` | Category grid with company counts |
| `review_submission.html` | `/sharh-yozish/` | Review form with company autocomplete |
| `review_edit.html` | — | Edit existing review |
| `review_delete_confirm.html` | — | Confirm review deletion |
| `user_profile.html` | `/profile/` | Edit profile, show own reviews and stats |
| `public_profile.html` | `/users/<username>/` | Read-only public profile |
| `manager_dashboard.html` | `/business-dashboard/` | Manager: pending reviews, managed companies |
| `manager_company_edit.html` | — | Edit company info |
| `manager_request_approval.html` | — | Request approval for review response |
| `manager_review_response.html` | — | Write response to a review |
| `company_claim.html` | — | Ownership claim form |
| `verification_badge.html` | — | Embeddable badge |
| `company_widget.html` | `/widget/<pk>/` | Embeddable rating widget |
| `widgets.html` | `/widgets/` | Widget installation guide |
| `report_review.html` | — | Abuse report form |
| `privacy_policy.html` | — | Privacy policy |
| `terms_of_service.html` | — | Terms of service |
| `community_guidelines.html` | — | Community guidelines |
| `contact_us.html` | — | Contact form |
| `ui_demo.html` | — | Internal UI component demo |

---

## 12. Static Files & Assets

- **Source:** `frontend/static/` and `public/`
- **Collection:** `python manage.py collectstatic` → `staticfiles/`
- **Serving:** WhiteNoise (`CompressedManifestStaticFilesStorage`) — serves gzip/brotli compressed files with content-hashed URLs
- **CSS:** `dist/bundle.css` (Tailwind CLI output) + `css/theme.css` (CSS variables, dark mode tokens)
- **Tailwind:** Also loaded from CDN (`cdn.tailwindcss.com`) for non-critical pages
- **Fonts:** Inter from Google Fonts (preconnect declared)
- **Favicons:** SVG, PNG, Apple touch icon, `manifest.json` (PWA)
- **PWA:** Service worker at `/service-worker.js`

### `static_bust` template tag
Custom tag that appends a cache-busting query string to static URLs. Defined in `frontend/templatetags/`.

---

## 13. i18n / Localisation

- **Languages:** Uzbek (`uz`, default) + Russian (`ru`)
- **URL scheme:** `/ru/...` prefix for Russian; no prefix for Uzbek (`prefix_default_language=False`)
- **Locale files:** `locale/uz/LC_MESSAGES/django.po` and `locale/ru/LC_MESSAGES/django.po`
- **DB translations:** `django-modeltranslation` for `BusinessCategory.name` and `Company.description` (uz/ru variants stored as separate DB columns)
- **Language detection:** `UzbekDefaultLocaleMiddleware` — strictly URL-based, browser headers ignored
- **`get_translated_url` tag:** Custom template tag in `frontend/templatetags/i18n_extras.py` that returns the current URL in the target language

### Translating strings
```bash
# Extract new strings
.venv/bin/python manage.py makemessages -l uz -l ru

# Compile after editing .po files
.venv/bin/python manage.py compilemessages
```

---

## 14. Authentication & Accounts

Powered by **django-allauth 65.11.2**.

- **Login methods:** username + password, email + password, Google OAuth 2.0
- **Signup fields:** `email*`, `username*`, `password1*`, `password2*`
- **Email verification:** Disabled (`ACCOUNT_EMAIL_VERIFICATION = "none"`)
- **Google OAuth:** PKCE enabled, `prompt=select_account`, scopes: `profile email`
- **Post-login redirect:** Preserved in session by `PostLoginRedirectMiddleware` and `handle_user_logged_in` signal
- **Custom adapter:** `frontend/adapters.py` — `AccountAdapter` and `SocialAccountAdapter`
- **Custom signup form:** `frontend/allauth_forms.py` — `CustomSignupForm`
- **Auto-approve:** `handle_user_signed_up` signal auto-sets `UserProfile.is_approved=True`

### Rate limits (env-overridable)
| Action | Default |
|---|---|
| `login` | 15 / 5 min |
| `login_failed` | 5 / 15 min |
| `signup` | 5 / 1 hour |
| `reset_password` | 5 / 1 hour |

---

## 15. Notifications (Email + Telegram)

### Email (`frontend/email_notifications.py`)
Class: `EmailNotificationService`

| Method | Trigger |
|---|---|
| `send_new_review_notification(company, review)` | After review created |
| `send_review_response_notification(review, response)` | After manager responds |
| `send_html_email(subject, template, context, to)` | Base helper |

Backend: SMTP in production (`EMAIL_BACKEND=smtp.EmailBackend`), console in debug. Allauth email subject prefix: `[Fikrly] ` (set via `ACCOUNT_EMAIL_SUBJECT_PREFIX`).

### Telegram (`frontend/utils.py` + `frontend/signals.py`)
- `send_telegram_review_notification(review)` — sends new review to `TELEGRAM_REVIEWS_CHAT_IDS` with inline Approve / Reject buttons (uses `sendPhoto` if receipt is attached, `sendMessage` otherwise)
- `send_telegram_message(chat_id, text)` — generic message sender
- `send_ownership_claim_notification(claim)` — notifies `TELEGRAM_ADMIN_CHAT_IDS`
- Webhook at `/api/tg/webhook/` handles button callbacks with HMAC token validation

---

## 16. Caching Strategy

### Backend
- **Redis** (`django-redis`) in production: `REDIS_URL=redis://redis:6379/1`
- **LocMemCache** in development (no Redis required)

### Cache layers
| Layer | Key pattern | TTL | Cleared by |
|---|---|---|---|
| Homepage (anon GET) | `home_page:{lang}` | 5 min | Review post_save signal |
| User-specific pages | `view:{user_id}:{path}:{query}` | 5 min | — |
| Public cache flush | All `home_page:*` keys | — | Admin action `clear_public_cache_action` |

### `cache_utils.py` decorators
- `@cache_per_user(timeout, key_prefix)` — per-user cache keyed on user ID + path + query
- `@cache_api_response(timeout, vary_on)` — JSON API response caching
- `clear_public_cache()` — deletes all `home_page:*` keys via Redis `SCAN`

---

## 17. Analytics (GA4 + GTM)

### Google Analytics 4
- Setting: `GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "")`
- Template: conditional `{% if GA_MEASUREMENT_ID %}` block in `base.html`
- Context: injected by `core.context_processors.google_analytics`

### Google Tag Manager
- Container ID: **GTM-WMVCCB9X**
- Setting: `GTM_ID = os.environ.get("GTM_ID", "GTM-WMVCCB9X")`
- Template head: `{% if GTM_ID %}` — GTM loader script as **first child of `<head>`**
- Template body: `{% if GTM_ID %}` — noscript iframe as **first child of `<body>`**
- Context: injected by same `core.context_processors.google_analytics`
- Deployed via: `GTM_ID=GTM-WMVCCB9X` in `.env` → `env_file` in `docker-compose.yml`

---

## 18. Management Commands

Located in `frontend/management/commands/`.

| Command | Purpose |
|---|---|
| `audit_links` | Crawl site and report broken links / 4xx/5xx responses |
| `clean_expired_exports` | Delete old `DataExport` files |
| `clear_reviews` | Remove test/spam reviews (dangerous — requires confirmation) |
| `fix_translations` | Back-fill missing translation fields in DB |
| `generate_sitemap` | Force-generate sitemap.xml to disk |
| `optimize_db` | Run `VACUUM ANALYZE` + `REINDEX` (PostgreSQL only) |
| `populate_translations` | Populate `uz`/`ru` translation fields from source |
| `register_telegram_webhook` | Register bot webhook URL with Telegram API |
| `seed_uzbek_data` | Seed demo categories and companies for development |
| `send_digest_emails` | Send weekly review digest to managers |
| `send_stats_report` | Send site statistics report via Telegram/email |
| `send_test_email` | Test SMTP configuration |
| `send_test_sms` | Test SMS gateway |
| `smtp_check` | Verify SMTP connection and credentials |

---

## 19. Docker & Infrastructure

### Services (`docker-compose.yml`)

| Service | Image | Role |
|---|---|---|
| `fikrly_web` | `./Dockerfile` (Python 3.12-slim, multi-stage) | Django + Gunicorn |
| `fikrly_nginx` | `nginx:1.25-alpine` | Reverse proxy, TLS, static/media |
| `fikrly_db` | `postgres:15-alpine` | Primary database |
| `fikrly_redis` | `redis:7-alpine` | Cache + sessions, `maxmemory 256mb allkeys-lru` |

### Dockerfile (multi-stage)
- **Stage 1 (builder):** Installs gcc, libpq-dev, all Python deps
- **Stage 2 (runtime):** Copies deps from builder, creates `appuser` (UID 1000), runs `collectstatic`
- Entrypoint: `docker/scripts/entrypoint.sh` (runs migrations, then starts gunicorn)

### Volumes
- `postgres_data` — PostgreSQL data directory
- `redis_data` — Redis persistence (append-only log)
- `static_volume` — Collected static files (shared with nginx)
- `media_volume` — User uploads (shared with nginx)
- `logs_volume` — Application logs

### Deployment workflow
```bash
# On the VPS, from /home/maymun/fikrly

# 1. Pull latest code
git pull origin main

# 2. Rebuild only the web image
sudo docker compose build web

# 3. Restart web container (zero nginx/db downtime)
sudo docker compose up -d --no-deps web

# 4. Verify
sudo docker inspect --format='{{.State.Health.Status}}' fikrly_web
sudo docker exec fikrly_web .venv/bin/python manage.py check
```

### Makefile shortcuts
```bash
make build          # docker compose build
make up             # docker compose up -d
make down           # docker compose down
make logs           # docker compose logs -f
make shell          # Django shell
make bash           # bash in web container
make migrate        # run migrations
make makemigrations # create migrations
make collectstatic  # collect static
make superuser      # create superuser
make backup         # backup DB + media
make clean          # remove containers + volumes (destructive)
```

---

## 20. Settings Reference

File: `myproject/settings.py` (598 lines).

| Setting | Default | Notes |
|---|---|---|
| `SECRET_KEY` | env `SECRET_KEY` | Must be set in production |
| `DEBUG` | `False` | env `DEBUG` |
| `ALLOWED_HOSTS` | env split | Always includes `fikrly.uz`, `www.fikrly.uz` |
| `DB_ENGINE` | `django.db.backends.postgresql` | SQLite allowed only in DEBUG |
| `REDIS_URL` | env | Falls back to `LocMemCache` if unset |
| `LANGUAGE_CODE` | `uz` | Site default language |
| `LANGUAGES` | `uz`, `ru` | Supported languages |
| `MODELTRANSLATION_DEFAULT_LANGUAGE` | `uz` | |
| `TIME_ZONE` | `UTC` | |
| `STATIC_URL` | `static/` | |
| `MEDIA_URL` | `/media/` | |
| `STATICFILES_STORAGE` | `CompressedManifestStaticFilesStorage` | WhiteNoise |
| `GA_MEASUREMENT_ID` | env | Google Analytics 4 — empty = disabled |
| `GTM_ID` | env, default `GTM-WMVCCB9X` | Google Tag Manager |
| `TELEGRAM_BOT_TOKEN` | env | Bot for moderation notifications |
| `TELEGRAM_ADMIN_CHAT_IDS` | env (comma-separated) | Admin chat IDs |
| `TELEGRAM_REVIEWS_CHAT_IDS` | env | Review notification chat IDs |
| `SITE_URL` | env, default `https://fikrly.uz` | Used in notification links |
| `SILK_ENABLED` | env / = DEBUG | Django Silk profiler |
| `SITE_ID` | env, default `2` | django.contrib.sites |

### Production security settings (when `DEBUG=False`)
- `SECURE_SSL_REDIRECT=True` (controllable via `USE_HTTPS`)
- `SECURE_HSTS_SECONDS=31536000` with subdomains + preload
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `X_FRAME_OPTIONS=DENY`
- `SECURE_CONTENT_TYPE_NOSNIFF=True`

---

## 21. Environment Variables

Stored in `.env` at project root. Loaded by `python-dotenv` in `settings.py`. Also consumed directly by `docker-compose.yml` via `env_file`.

### Required in production
```
SECRET_KEY=<long-random-string>
DB_PASSWORD=<postgres-password>
ALLOWED_HOSTS=fikrly.uz,www.fikrly.uz
```

### Analytics
```
GA_MEASUREMENT_ID=G-VF0K77S81T
GTM_ID=GTM-WMVCCB9X
```

### Email
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=fikrlyuzb@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
DEFAULT_FROM_EMAIL=fikrlyuzb@gmail.com
```

### Telegram
```
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_ADMIN_CHAT_IDS=-4923806324
TELEGRAM_REVIEWS_CHAT_IDS=<chat-id>
TELEGRAM_WEBHOOK_SECRET=<auto-derived-from-token>
```

### Database
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=fikrly_db
DB_USER=fikrly_user
DB_PASSWORD=<password>
DB_HOST=db
DB_PORT=5432
```

### Optional
```
DEBUG=False
REDIS_URL=redis://redis:6379/1
SITE_URL=https://fikrly.uz
SILK_ENABLED=False
USE_HTTPS=True
```

---

## 22. Testing

### Unit/integration tests
- Location: `frontend/tests/`
- Runner: `python manage.py test`
- Settings override: `myproject/settings_test.py`

### E2E tests
- Location: `tests/` (root)
- Framework: **Playwright** (`playwright.config.js`)
- Settings override: `myproject/settings_e2e.py` (uses `db_e2e.sqlite3`)

```bash
# Unit tests
.venv/bin/python manage.py test frontend

# E2E tests
npx playwright test
```

---

## 23. Deployment Runbook

### First-time server setup
```bash
git clone https://github.com/khdrvss/fikrly /home/maymun/fikrly
cd /home/maymun/fikrly
cp .env.example .env       # Edit with production values
sudo bash deploy/initial_setup.sh
```

### Regular deployment
```bash
git pull origin main
sudo docker compose build web
sudo docker compose up -d --no-deps web
```

### Database backup
```bash
sudo bash deploy/backup.sh
# Or via make:
make backup
```

### SSL renewal
```bash
sudo bash deploy/ssl_renew.sh
```

### View logs
```bash
# All services
sudo docker compose logs -f

# Just web
sudo docker compose logs -f web

# Application log file
sudo docker exec fikrly_web tail -f /app/logs/django.log
```

### Emergency cache flush
Via Django admin → CompanyAdmin → select any company → Actions → "Clear public cache"

Or programmatically:
```bash
sudo docker exec fikrly_web .venv/bin/python manage.py shell -c "from frontend.cache_utils import clear_public_cache; print(clear_public_cache())"
```

---

## 24. Known Issues & TODOs

| Priority | Item | File |
|---|---|---|
| ~~P2~~ | ~~`email_notifications.py` imports `from celery import shared_task`~~ ✅ **FIXED** — import removed | `frontend/email_notifications.py` |
| ~~P2~~ | ~~Remove obsolete `version:` key from `docker-compose.yml`~~ ✅ **Already absent** | `docker-compose.yml` |
| ~~P2~~ | ~~`/health/` endpoint not wired~~ ✅ **FIXED** — wired in `myproject/urls.py`, `SECURE_REDIRECT_EXEMPT` added | `myproject/urls.py` |
| P2 | **Sentry** error tracking not configured — no visibility into production exceptions | `myproject/settings.py` |
| P2 | **Google Search Console** verification meta tag missing — Bing/Yandex done | `frontend/templates/base.html` |
| P2 | **Celery + Beat** not installed — emails sent synchronously (blocks request cycle) | `requirements.txt` |
| P3 | `myproject/urls.py` imports `debug_toolbar` inside `if settings.DEBUG` — if package removed from deps will raise `ImportError` at startup | `myproject/urls.py` |
| P3 | `GTM_ID` default hardcoded in `settings.py` — consider removing it and relying solely on `.env` for stricter 12-factor config | `myproject/settings.py` |
| P3 | `company_detail` view increments `view_count` on every session — already session-gated but consider analytics-only approach | `frontend/views/company.py` |
