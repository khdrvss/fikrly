"""
frontend.views package
======================
This package replaces the monolithic views.py file.

Sub-modules:
  company  – business listings, detail, dashboard, claims, likes
  review   – review submission, editing, deletion, votes
  profile  – user and public profile pages
  misc     – static pages, language switch, system utilities
"""

from .company import (
    home,
    homepage,
    business_dashboard,
    business_profile,
    manager_company_edit,
    manager_request_approval,
    search_suggestions_api,
    business_list,
    category_browse,
    claim_company,
    verify_claim,
    verification_badge,
    company_detail,
    reveal_contact,
    like_company,
    submit_ownership_claim,
    admin_approve_claim,
    admin_reject_claim,
    telegram_claim_webhook,
    company_widget,
)

from .review import (
    review_submission,
    manager_review_response,
    report_review,
    like_review,
    vote_review_helpful,
    review_edit,
    review_delete,
)

from .profile import (
    user_profile,
    public_profile,
)

from .misc import (
    safe_set_language,
    privacy_policy,
    terms_of_service,
    community_guidelines,
    contact_us,
    robots_txt,
    bing_site_auth,
    favicon_file,
    service_worker,
    health_check,
    ratelimit_error,
    widgets_page,
)

__all__ = [
    # company
    "home",
    "homepage",
    "business_dashboard",
    "business_profile",
    "manager_company_edit",
    "manager_request_approval",
    "search_suggestions_api",
    "business_list",
    "category_browse",
    "claim_company",
    "verify_claim",
    "verification_badge",
    "company_detail",
    "reveal_contact",
    "like_company",
    # review
    "review_submission",
    "manager_review_response",
    "report_review",
    "like_review",
    "vote_review_helpful",
    "review_edit",
    "review_delete",
    # profile
    "user_profile",
    "public_profile",
    # misc
    "safe_set_language",
    "privacy_policy",
    "terms_of_service",
    "community_guidelines",
    "contact_us",
    "robots_txt",
    "bing_site_auth",
    "favicon_file",
    "service_worker",
    "health_check",
    "ratelimit_error",
    "widgets_page",
]
