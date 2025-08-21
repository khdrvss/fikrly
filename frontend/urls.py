from django.urls import path
from .views import category_browse, home, user_profile, review_submission, business_dashboard, business_profile, homepage
from frontend import views

urlpatterns = [
    path('', views.home, name='index'),
    path('profile/', user_profile, name='user_profile'),
    path('submit-review/', review_submission, name='review_submission'),
    path('business-dashboard/', business_dashboard, name='business_dashboard'),
    path('business-profile/', business_profile, name='business_profile'),
    path('category-browse/', category_browse, name='category_browse'),
    #path('homepage/', homepage, name='homepage'),
    path('review-submission/', review_submission, name='review_submission'),
    path('user-profile/', user_profile, name='user_profile'),

]