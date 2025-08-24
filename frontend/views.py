from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.decorators import login_required
from .models import Company, Review

# Create your views here.
def home(request):
    top_companies = Company.objects.order_by('-rating')[:6]
    trending = Company.objects.order_by('-review_count')[:6]
    latest_reviews = Review.objects.select_related('company').all()[:6]
    ctx = {
        'top_companies': top_companies,
        'trending_companies': trending,
        'latest_reviews': latest_reviews,
    }
    return render(request, 'pages/home.html', ctx)

@login_required
def business_dashboard(request):
    return render(request, 'pages/business_dashboard.html')

def business_profile(request):
    return render(request, 'pages/business_profile.html')

def category_browse(request):
    return render(request, 'pages/category_browse.html')

def homepage(request):
    return render(request, 'pages/home.html')

class ReviewForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label="Kompaniya tanlang")

    class Meta:
        model = Review
        fields = ['company', 'user_name', 'rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'text': forms.Textarea(attrs={'rows': 4}),
        }


def review_submission(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review: Review = form.save(commit=False)
            review.verified_purchase = True
            review.save()
            # Update company counters
            company = review.company
            company.review_count = company.reviews.count()
            company.rating = round(sum(r.rating for r in company.reviews.all()) / company.review_count, 2)
            company.save()
            return redirect('index')
    else:
        form = ReviewForm()
    return render(request, 'pages/review_submission.html', {'form': form})

@login_required
def user_profile(request):
    return render(request, 'pages/user_profile.html')