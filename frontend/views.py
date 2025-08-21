from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'pages/home.html')

def business_dashboard(request):
    return render(request, 'frontend/pages/business_dashboard.html')

def business_profile(request):
    return render(request, 'frontend/pages/business_profile.html')

def category_browse(request):
    return render(request, 'frontend/pages/category_browse.html')

def homepage(request):
    return render(request, 'frontend/pages/homepage.html')

def review_submission(request):
    return render(request, 'frontend/pages/review_submission.html')

def user_profile(request):
    return render(request, 'frontend/pages/user_profile.html')