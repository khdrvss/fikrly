from django.urls import path
from .views import (
    category_browse, home, user_profile, review_submission, business_dashboard,
    business_profile, business_list, company_detail, search_businesses,
    review_edit, review_delete, privacy_policy, terms_of_service, community_guidelines,
    manager_company_edit, manager_request_approval, report_review, manager_review_response,
    claim_company, verify_claim, verification_badge
)
from frontend import views

urlpatterns = [
    path('', views.home, name='index'),
    path('profile/', user_profile, name='user_profile'),
    path('business-dashboard/', business_dashboard, name='business_dashboard'),
    path('manager/company/<int:pk>/edit/', manager_company_edit, name='manager_company_edit'),
    path('manager/reviews/<int:pk>/request-approval/', manager_request_approval, name='manager_request_approval'),
    path('manager/reviews/<int:pk>/respond/', manager_review_response, name='manager_review_response'),
    path('business-profile/', business_profile, name='business_profile'),
    path('business-list/', business_list, name='business_list'),
    path('search/', search_businesses, name='search_businesses'),
    path('business/<int:pk>/', company_detail, name='company_detail'),
    path('business/<int:pk>/reveal/<str:kind>/', views.reveal_contact, name='reveal_contact'),
    path('business/<int:pk>/like/', views.like_company, name='like_company'),
    path('business/<int:pk>/claim/', claim_company, name='claim_company'),
    path('claim/verify/<str:token>/', verify_claim, name='verify_claim'),
    path('verification-badge/', verification_badge, name='verification_badge'),
    path('reviews/<int:pk>/report/', report_review, name='report_review'),
    path('category-browse/', category_browse, name='category_browse'),
    path('review-submission/', review_submission, name='review_submission'),
    path('reviews/<int:pk>/edit/', review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', review_delete, name='review_delete'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('terms/', terms_of_service, name='terms_of_service'),
    path('guidelines/', community_guidelines, name='community_guidelines'),
    # Phone OTP auth
    path('accounts/phone/', views.phone_signin, name='phone_signin'),
    path('accounts/phone/verify/', views.phone_verify, name='phone_verify'),
]