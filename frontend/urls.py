from django.urls import path
from django.views.generic import RedirectView
from django.shortcuts import render
from .views import (
    category_browse,
    user_profile,
    review_submission,
    business_dashboard,
    business_profile,
    business_list,
    company_detail,
    review_edit,
    review_delete,
    privacy_policy,
    terms_of_service,
    community_guidelines,
    manager_company_edit,
    manager_request_approval,
    report_review,
    manager_review_response,
    claim_company,
    verify_claim,
    verification_badge,
)
from frontend import views
from frontend import advanced_views
from frontend import moderation_views

urlpatterns = [
    path("", views.home, name="index"),
    path("profile/", user_profile, name="user_profile"),
    path("users/<str:username>/", views.public_profile, name="public_profile"),
    path("business-dashboard/", business_dashboard, name="business_dashboard"),
    path(
        "manager/company/<int:pk>/edit/",
        manager_company_edit,
        name="manager_company_edit",
    ),
    path(
        "manager/reviews/<int:pk>/request-approval/",
        manager_request_approval,
        name="manager_request_approval",
    ),
    path(
        "manager/reviews/<int:pk>/respond/",
        manager_review_response,
        name="manager_review_response",
    ),
    path("business-profile/", business_profile, name="business_profile"),
    # New SEO-friendly paths
    path("bizneslar/", business_list, name="business_list"),
    path("businesses/", business_list, name="business_list_en"),
    path("kategoriyalar/", category_browse, name="category_browse"),
    path(
        "kategoriyalar/<slug:category_slug>/",
        business_list,
        name="business_list_by_category",
    ),
    path("sharh-yozish/", review_submission, name="review_submission"),
    # Redirects for old paths (301 Permanent)
    path(
        "business-list/",
        RedirectView.as_view(
            pattern_name="business_list", permanent=True, query_string=True
        ),
    ),
    path(
        "category-browse/",
        RedirectView.as_view(
            pattern_name="category_browse", permanent=True, query_string=True
        ),
    ),
    path(
        "review-submission/",
        RedirectView.as_view(
            pattern_name="review_submission", permanent=True, query_string=True
        ),
    ),
    path("search/", business_list, name="search_businesses"),
    path(
        "api/search-suggestions/",
        views.search_suggestions_api,
        name="search_suggestions_api",
    ),
    path("business/<int:pk>/", company_detail, name="company_detail"),
    path(
        "business/<int:pk>/reveal/<str:kind>/",
        views.reveal_contact,
        name="reveal_contact",
    ),
    path("business/<int:pk>/like/", views.like_company, name="like_company"),
    path("reviews/<int:pk>/like/", views.like_review, name="like_review"),
    path("api/reviews/<int:pk>/vote/", views.vote_review_helpful, name="vote_review_helpful"),
    path("business/<int:pk>/claim/", claim_company, name="claim_company"),
    path("claim/verify/<str:token>/", verify_claim, name="verify_claim"),
    path("verification-badge/", verification_badge, name="verification_badge"),
    path("reviews/<int:pk>/report/", report_review, name="report_review"),
    path("reviews/<int:pk>/edit/", review_edit, name="review_edit"),
    path("reviews/<int:pk>/delete/", review_delete, name="review_delete"),
    path("privacy/", privacy_policy, name="privacy_policy"),
    path("terms/", terms_of_service, name="terms_of_service"),
    path("guidelines/", community_guidelines, name="community_guidelines"),
    path("contact/", views.contact_us, name="contact_us"),
    # UI Demo (development only)
    path("ui-demo/", lambda request: render(request, "pages/ui_demo.html"), name="ui_demo"),
    # Phone OTP auth
    path("accounts/phone/", views.phone_signin, name="phone_signin"),
    path("accounts/phone/verify/", views.phone_verify, name="phone_verify"),
    # PWA offline page
    path("offline/", lambda request: render(request, "frontend/offline.html"), name="offline"),
    # Analytics dashboard
    path("business/<int:company_id>/analytics/", advanced_views.analytics_dashboard, name="analytics_dashboard"),
    # Gamification
    path("gamification/profile/", advanced_views.user_gamification_profile, name="gamification_profile"),
    # Two-Factor Authentication
    path("security/2fa/setup/", advanced_views.setup_2fa, name="setup_2fa"),
    path("security/2fa/verify/", advanced_views.verify_2fa, name="verify_2fa"),
    # Advanced Search
    path("advanced-search/", advanced_views.advanced_search, name="advanced_search"),
    # Review Images
    path("reviews/<int:review_id>/upload-images/", advanced_views.upload_review_images, name="upload_review_images"),
    # Moderation Dashboard
    path("admin/moderation/", moderation_views.moderation_dashboard, name="moderation_dashboard"),
    path("admin/moderation/bulk/", moderation_views.bulk_moderate_reviews, name="bulk_moderate_reviews"),
    path("reviews/<int:review_id>/flag/", moderation_views.flag_review, name="flag_review"),
    path("admin/flags/<int:flag_id>/resolve/", moderation_views.resolve_flag, name="resolve_flag"),
    # Business Verification
    path("business/<int:company_id>/request-verification/", moderation_views.request_verification, name="request_verification"),
    path("admin/business/<int:company_id>/verify/", moderation_views.approve_verification, name="approve_verification"),
    # Data Export
    path("export/reviews-pdf/<int:company_id>/", moderation_views.export_reviews_pdf, name="export_reviews_pdf"),
    path("export/reviews-excel/<int:company_id>/", moderation_views.export_reviews_excel, name="export_reviews_excel"),
    path("export/user-data/", moderation_views.export_user_data, name="export_user_data"),
    path("export/request/", moderation_views.request_data_export, name="request_data_export"),
    # Utility
    path("health/", views.health_check, name="health_check"),
]
