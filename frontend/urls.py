from django.urls import path
from .views import category_browse, home, user_profile, review_submission, business_dashboard, business_profile, business_list, company_detail, search_businesses
from frontend import views

urlpatterns = [
    path('', views.home, name='index'),
    path('profile/', user_profile, name='user_profile'),
    path('business-dashboard/', business_dashboard, name='business_dashboard'),
    path('business-profile/', business_profile, name='business_profile'),
    path('business-list/', business_list, name='business_list'),
    path('search/', search_businesses, name='search_businesses'),
    path('business/<int:pk>/', company_detail, name='company_detail'),
    path('category-browse/', category_browse, name='category_browse'),
    path('review-submission/', review_submission, name='review_submission'),
]