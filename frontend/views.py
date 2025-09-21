from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from .models import Company, Review
from .utils import compute_assessment
import json
from pathlib import Path


# Create your views here.
class ReviewForm(forms.ModelForm):
	company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label="Kompaniya tanlang", widget=forms.Select(attrs={'class': 'input-field'}))

	class Meta:
		model = Review
		fields = ['company', 'user_name', 'rating', 'text']
		widgets = {
			'user_name': forms.TextInput(attrs={'class': 'input-field'}),
			'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'input-field'}),
			'text': forms.Textarea(attrs={'rows': 4, 'class': 'input-field h-32 resize-none'}),
		}


def _load_category_labels() -> dict:
	data_path = Path(__file__).resolve().parent / 'data' / 'categories_uz.json'
	try:
		with open(data_path, 'r', encoding='utf-8') as f:
			return json.load(f)
	except Exception:
		return {}


def home(request):
	top_companies = Company.objects.order_by('-rating')[:6]
	trending = Company.objects.order_by('-review_count')[:6]
	latest_reviews = Review.objects.select_related('company').all()[:6]
	# attach assessments for display if needed later
	for c in trending:
		c.assessment = compute_assessment(float(c.rating), int(c.review_count))
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
	"""Redirect to business list - shows all businesses as cards"""
	return redirect('business_list')

def search_businesses(request):
	"""Dedicated search view for home page search"""
	query = request.GET.get('q', '').strip()
	companies = Company.objects.all()
	
	if query:
		# Enhanced search with multiple field matching
		companies = companies.filter(
			Q(name__icontains=query) | 
			Q(city__icontains=query) | 
			Q(category__icontains=query) |
			Q(description__icontains=query)
		)
		
		# If no results, try partial matching for better user experience
		if not companies.exists():
			# Try splitting query into words for partial matching
			words = query.split()
			if len(words) > 1:
				for word in words:
					if len(word) > 2:  # Only search for words longer than 2 characters
						partial_results = Company.objects.filter(
							Q(name__icontains=word) | 
							Q(category__icontains=word)
						)
						if partial_results.exists():
							companies = partial_results
							break
	
	companies = companies.order_by('-review_count', '-rating', 'name')
	
	# Get search suggestions for better UX
	search_suggestions = []
	if query and not companies.exists():
		# Suggest popular categories and cities
		popular_categories = Company.objects.values_list('category', flat=True).distinct()[:5]
		popular_cities = Company.objects.values_list('city', flat=True).distinct()[:5]
		
		search_suggestions = {
			'categories': list(popular_categories),
			'cities': list(popular_cities)
		}
	
	return render(request, 'pages/business_list.html', { 
		'companies': companies,
		'search_query': query,
		'search_results_count': companies.count(),
		'search_suggestions': search_suggestions
	})

def business_list(request):
	"""View that lists all businesses as clickable cards"""
	companies = Company.objects.all()
	query = request.GET.get('q', '')
	category_filter = request.GET.get('category', '')
	
	if query:
		companies = companies.filter(
			Q(name__icontains=query) | Q(city__icontains=query) | Q(category__icontains=query)
		)
	
	if category_filter:
		companies = companies.filter(category__iexact=category_filter)
	
	companies = companies.order_by('-review_count', '-rating', 'name')
	
	# Set search context
	search_context = query or category_filter
	search_display = query if query else f"Kategoriya: {category_filter}" if category_filter else ""
	
	return render(request, 'pages/business_list.html', { 
		'companies': companies,
		'search_query': search_context,
		'search_results_count': companies.count(),
		'category_filter': category_filter,
		'search_display': search_display
	})


def category_browse(request):
	labels = _load_category_labels()
	
	# Get all unique categories
	categories_qs = (
		Company.objects.exclude(category="").order_by('category').values_list('category', flat=True).distinct()
	)
	
	# Dynamic category cards based on real data
	category_stats = (
		Company.objects.values('category')
		.annotate(avg_rating=Avg('reviews__rating'), total_reviews=Count('reviews'))
		.order_by('category')
	)
	category_cards = []
	for item in category_stats:
		cat_key = item['category'] or 'Boshqa'
		cat_label = labels.get(cat_key, cat_key)
		review_count = int(item['total_reviews'] or 0)
		avg_rating = float(item['avg_rating'] or 0)
		assessment = compute_assessment(avg_rating, review_count)
		rep = Company.objects.filter(category=cat_key).order_by('-review_count', '-rating').first()
		badge_text = f"{review_count} sharh"
		category_cards.append({
			'category': cat_key,
			'label': cat_label,
			'image_url': getattr(rep, 'image_url', '') if rep else '',
			'badge_text': badge_text,
			'popular_company': rep.name if rep else '',
			'popular_rating': rep.rating if rep else 0,
			'assessment': assessment,
		})

	return render(request, 'pages/category_browse.html', {
		'category_cards': category_cards,
	})


def homepage(request):
	return render(request, 'pages/home.html')


def review_submission(request):
	"""
	Create a new review.
	- Supports optional ?company=<id> to preselect a company.
	- Validates rating in [1,5].
	- Recalculates company rating and review_count using DB aggregates for accuracy.
	- On success, redirects to the company detail page; otherwise re-renders with errors.
	"""
	preselected_company_id = request.GET.get('company')
	initial = {}
	if preselected_company_id and preselected_company_id.isdigit():
		try:
			initial['company'] = Company.objects.get(pk=int(preselected_company_id))
		except Company.DoesNotExist:
			pass

	if request.method == 'POST':
		form = ReviewForm(request.POST)
		# Extra server-side validation for rating bounds
		try:
			rating_val = int(request.POST.get('rating', 0))
			if not 1 <= rating_val <= 5:
				form.add_error('rating', 'Baho 1 dan 5 gacha bo\'lishi kerak.')
		except (TypeError, ValueError):
			form.add_error('rating', 'To\'g\'ri baho kiriting (1-5).')

		if form.is_valid():
			review: Review = form.save(commit=False)
			review.verified_purchase = True
			review.save()

			# Update company stats using DB-level aggregation to avoid race conditions
			company = review.company
			agg = company.reviews.aggregate(avg=Avg('rating'), cnt=Count('id'))
			company.review_count = int(agg.get('cnt') or 0)
			company.rating = round(float(agg.get('avg') or 0.0), 2) if company.review_count else 0
			company.save(update_fields=['review_count', 'rating'])

			return redirect('company_detail', pk=company.pk)
	else:
		form = ReviewForm(initial=initial)

	# Provide all companies for the inline picker (scrollable + client-side filter)
	# Ordered by popularity first for convenience
	suggested_companies = Company.objects.order_by('-review_count', '-rating', 'name')

	return render(request, 'pages/review_submission.html', {
		'form': form,
		'suggested_companies': suggested_companies,
	})


def company_detail(request, pk: int):
	company = Company.objects.get(pk=pk)
	company.assessment = compute_assessment(float(company.rating), int(company.review_count))
	reviews = company.reviews.all()
	return render(request, 'pages/company_detail.html', {
		'company': company,
		'reviews': reviews,
	})


@login_required
def user_profile(request):
	return render(request, 'pages/user_profile.html')