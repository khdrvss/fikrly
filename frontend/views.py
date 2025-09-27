from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from .models import Company, Review, UserProfile
from .utils import compute_assessment, send_telegram_message, diff_instance_fields
import json
from pathlib import Path
from .forms import ProfileForm
from django.http import Http404, JsonResponse
from django.contrib import messages
from .forms import ReviewEditForm
from .forms import CompanyManagerEditForm, ReviewApprovalRequestForm, ReportReviewForm, OwnerResponseForm
from django.contrib.auth import login
from django.core.cache import cache
from django.utils.timezone import now
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import PhoneOTP
from .sms import send_otp_via_eskiz
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from datetime import timedelta
from .forms import ClaimCompanyForm
from .models import CompanyClaim, ActivityLog
from .models import CompanyLike


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
	# If user just authenticated and no explicit redirect handled yet, nudge to profile once
	if request.user.is_authenticated and not request.session.get('_redirected_once'):
		request.session['_next_after_login'] = request.session.get('_next_after_login', '/profile/')
		request.session['_redirected_once'] = True
	return render(request, 'pages/home.html', ctx)


@login_required
def business_dashboard(request):
	# Manager dashboard: show companies managed by the user and pending reviews
	companies = Company.objects.filter(manager=request.user)
	pending_reviews = Review.objects.filter(company__manager=request.user, is_approved=False).select_related('company')
	return render(request, 'pages/manager_dashboard.html', {
		'companies': companies,
		'pending_reviews': pending_reviews,
	})


def business_profile(request):
	"""Redirect to business list - shows all businesses as cards"""
	return redirect('business_list')


@login_required
def manager_company_edit(request, pk: int):
	try:
		company = Company.objects.get(pk=pk, manager=request.user)
	except Company.DoesNotExist:
		raise Http404

	if request.method == 'POST':
		form = CompanyManagerEditForm(request.POST, request.FILES, instance=company)
		if form.is_valid():
			obj = form.save()
			# Log activity
			from .models import ActivityLog
			changed = {k: form.cleaned_data.get(k) for k in form.changed_data}
			ActivityLog.objects.create(
				actor=request.user,
				action='company_edit',
				company=obj,
				details=diff_instance_fields(obj, changed),
			)
			messages.success(request, 'Kompaniya maʼlumotlari yangilandi.')
			return redirect('business_dashboard')
	else:
		form = CompanyManagerEditForm(instance=company)

	return render(request, 'pages/manager_company_edit.html', {
		'form': form,
		'company': company,
	})

@login_required
def manager_request_approval(request, pk: int):
	try:
		review = Review.objects.select_related('company').get(pk=pk, company__manager=request.user)
	except Review.DoesNotExist:
		raise Http404

	if request.method == 'POST':
		form = ReviewApprovalRequestForm(request.POST)
		if form.is_valid():
			review.approval_requested = True
			review.save(update_fields=['approval_requested'])
			# Log + notify
			from .models import ActivityLog
			ActivityLog.objects.create(
				actor=request.user,
				action='approval_requested',
				company=review.company,
				review=review,
				details=f"Review #{review.pk} approval requested",
			)
			send_telegram_message((
				f"<b>Approval requested</b>\n"
				f"Company: {review.company.name}\n"
				f"By: {request.user.username}\n"
				f"Review #{review.pk} — {review.rating}⭐\n"
				f"{review.text[:180]}..."
			))
			messages.success(request, 'Tasdiqlash so‘rovi yuborildi. Adminlar ko‘rib chiqishadi.')
			return redirect('business_dashboard')
	else:
		form = ReviewApprovalRequestForm()

	return render(request, 'pages/manager_request_approval.html', {
		'form': form,
		'review': review,
	})

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
			words = query.split()
			if len(words) > 1:
				for word in words:
					if len(word) > 2:
						partial_results = Company.objects.filter(
							Q(name__icontains=word) | Q(category__icontains=word)
						)
						if partial_results.exists():
							companies = partial_results
							break
	
	companies = companies.order_by('-review_count', '-rating', 'name')
	
	# Get search suggestions for better UX
	search_suggestions = []
	if query and not companies.exists():
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


def _get_category_icons():
	"""Returns category-specific icons mapping"""
	return {
		'Aviatsiya': '<path d="M21 16V4.58C21 4.21 20.81 3.85 20.49 3.62C20.17 3.38 19.73 3.28 19.3 3.34L3.3 5.35C2.67 5.44 2.25 6.03 2.25 6.7V16C2.25 16.69 2.81 17.25 3.5 17.25H21C21.41 17.25 21.75 16.91 21.75 16.5C21.75 16.09 21.41 15.75 21 15.75V16Z"/>',
		'Bank': '<path d="M12 2L3 7V8H21V7L12 2Z"/><path d="M4 9V19H20V9"/><path d="M8 15V13H10V15H8Z"/><path d="M14 15V13H16V15H14Z"/>',
		'Ichimliklar': '<path d="M5 12V7L7 5H17L19 7V12"/><path d="M5 12L2 22H22L19 12"/><path d="M12 5V2"/>',
		'Eksport, logistika': '<path d="M14 18V6C14 5.45 13.55 5 13 5H11C10.45 5 10 5.45 10 6V18L7 21L12 19L17 21L14 18Z"/>',
		'Energetika': '<path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/>',
		'Fast-food': '<path d="M8.5 8.5C9.33 8.5 10 7.83 10 7S9.33 5.5 8.5 5.5 7 6.17 7 7 7.67 8.5 8.5 8.5Z"/><path d="M12 2C10.89 2 10 2.89 10 4V7C10 8.11 10.89 9 12 9S14 8.11 14 7V4C14 2.89 13.11 2 12 2Z"/><path d="M5 9V20C5 21.1 5.9 22 7 22H17C18.1 22 19 21.1 19 20V9H5Z"/>',
		'Fintech': '<path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4H20C20.55 4 21 4.45 21 5S20.55 6 20 6H19V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V6H4C3.45 6 3 5.55 3 5S3.45 4 4 4H7Z"/>',
		'IT, Konsalting': '<path d="M20 3H4C2.9 3 2 3.9 2 5V19C2 20.1 2.9 21 4 21H20C21.1 21 22 20.1 22 19V5C22 3.9 21.1 3 20 3Z"/><path d="M8 17L12 13L16 17"/>',
		'IT, Raqamli marketing': '<path d="M12 2L13.09 8.26L22 9L13.09 15.74L12 22L10.91 15.74L2 9L10.91 8.26L12 2Z"/>',
		'IT, Texnologiya': '<path d="M9 12L11 14L15 10"/><path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12S7.03 3 12 3S21 7.03 21 12Z"/>',
		'Kimyo sanoati': '<path d="M10.5 2L8.5 8H15.5L13.5 2H10.5Z"/><path d="M7 8L5 16C4.72 17.2 5.54 18.36 6.76 18.64L17.24 18.64C18.46 18.36 19.28 17.2 19 16L17 8H7Z"/>',
		'Ko\'chmas mulk': '<path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z"/>',
		'Konchilik va metallurgiya': '<path d="M12 2L15.09 8.26L22 9L16 14.74L17.18 21.02L12 18.77L6.82 21.02L8 14.74L2 9L8.91 8.26L12 2Z"/>',
		'Metallurgiya': '<path d="M9 11H15L13 13L15 15H9L11 13L9 11Z"/><path d="M12 2L22 8.5V15.5L12 22L2 15.5V8.5L12 2Z"/>',
		'Mobil operator': '<path d="M22 16.92V19.92C22 20.51 21.39 21 20.92 21C18.95 20.87 16.95 20.22 15.21 19.27C13.15 18.15 11.26 16.26 10.14 14.2C9.19 12.46 8.54 10.46 8.41 8.49C8.4 8.18 8.56 7.65 9.01 7.65H12.01"/><path d="M18 2L22 6L18 10"/><path d="M14 6H22"/>',
		'Nodavlat notijorat tashkiloti': '<path d="M12 2L3.5 6.5V17.5L12 22L20.5 17.5V6.5L12 2Z"/><path d="M12 8C13.66 8 15 6.66 15 5S13.66 2 12 2S9 3.34 9 5S10.34 8 12 8Z"/>',
		'Neft va gaz': '<path d="M9 2V13C9 14.1 9.9 15 11 15H13C14.1 15 15 14.1 15 13V2H9Z"/><path d="M12 15V22"/>',
		'Oziq-ovqat ishlab chiqarish': '<path d="M12 2C6.48 2 2 6.48 2 12S6.48 22 12 22 22 17.52 22 12 17.52 2 12 2Z"/><path d="M8 12L11 15L16 10"/>',
		'Oziq-ovqat yetkazib berish': '<path d="M4 16L20 16"/><path d="M4 16L8 12"/><path d="M4 16L8 20"/>',
		'Supermarket': '<path d="M7 4V2C7 1.45 7.45 1 8 1H16C16.55 1 17 1.45 17 2V4"/><path d="M5 7H19L18 17H6L5 7Z"/><path d="M5 7L3 4"/>',
		'Tashqi savdo': '<path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12S7.03 3 12 3S21 7.03 21 12Z"/><path d="M8 12L11 15L16 10"/>',
		'Test 1 sharh': '<path d="M14 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/><path d="M14 2V8H20"/>',
		'Telekommunikatsiya': '<path d="M6.62 10.79C8.06 13.62 10.38 15.94 13.21 17.38L15.41 15.18C15.69 14.9 16.08 14.82 16.43 14.93C17.55 15.3 18.75 15.5 20 15.5C20.55 15.5 21 15.95 21 16.5V20C21 20.55 20.55 21 20 21A17 17 0 0 1 3 4C3 3.45 3.45 3 4 3H7.5C8.05 3 8.5 3.45 8.5 4C8.5 5.25 8.7 6.45 9.07 7.57C9.18 7.92 9.1 8.31 8.82 8.59L6.62 2.79V10.79Z"/>',
		'To\'qimachilik': '<path d="M12 2L2 7L12 12L22 7L12 2Z"/><path d="M2 17L12 22L22 17"/><path d="M2 12L12 17L22 12"/>'
	}

def category_browse(request):
	from .models import Category
	
	# Get all active categories from the database
	db_categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
	
	# Get all unique categories from companies (for backwards compatibility)
	labels = _load_category_labels()
	category_icons = _get_category_icons()
	
	category_stats = (
		Company.objects.values('category')
		.annotate(avg_rating=Avg('reviews__rating'), total_reviews=Count('reviews'), company_count=Count('id'))
		.order_by('category')
	)
	
	# Create category list
	categories = []
	
	# First, add categories from the Category model
	for db_cat in db_categories:
		# Find matching company stats
		stats = next((item for item in category_stats if item['category'] == db_cat.name), None)
		
		review_count = int(stats['total_reviews'] or 0) if stats else 0
		company_count = int(stats['company_count'] or 0) if stats else 0
		avg_rating = float(stats['avg_rating'] or 0) if stats else 0
		
		categories.append({
			'category': db_cat.slug,
			'label': db_cat.name,
			'icon': db_cat.icon_svg or '<path d="M12 2L2 7L12 12L22 7L12 2Z"/>',
			'color': db_cat.color,
			'description': db_cat.description,
			'review_count': review_count,
			'company_count': company_count,
			'avg_rating': round(avg_rating, 1) if avg_rating > 0 else 0,
			'from_db': True,
		})
	
	# Then add any remaining categories from company data that aren't in Category model
	db_category_names = {cat.name for cat in db_categories}
	
	for item in category_stats:
		cat_key = item['category'] or 'Boshqa'
		if cat_key == 'Boshqa' or not cat_key or cat_key in db_category_names:
			continue
			
		cat_label = labels.get(cat_key, cat_key)
		review_count = int(item['total_reviews'] or 0)
		company_count = int(item['company_count'] or 0)
		avg_rating = float(item['avg_rating'] or 0)
		
		# Get icon for this category
		icon = category_icons.get(cat_key, '<path d="M12 2L2 7L12 12L22 7L12 2Z"/>')
		
		categories.append({
			'category': cat_key,
			'label': cat_label,
			'icon': icon,
			'color': 'gray',
			'description': '',
			'review_count': review_count,
			'company_count': company_count,
			'avg_rating': round(avg_rating, 1) if avg_rating > 0 else 0,
			'from_db': False,
		})

	return render(request, 'pages/category_browse.html', {
		'categories': categories,
	})


def homepage(request):
	return render(request, 'pages/home.html')


@login_required
def claim_company(request, pk: int):
	try:
		company = Company.objects.get(pk=pk)
	except Company.DoesNotExist:
		raise Http404

	# If already managed/verified, block
	if company.manager_id and company.manager_id != request.user.id:
		messages.error(request, 'Bu kompaniya allaqachon boshqarilmoqda.')
		return redirect('company_detail', pk=company.pk)

	if request.method == 'POST':
		form = ClaimCompanyForm(request.POST, company=company)
		if form.is_valid():
			email = form.cleaned_data['email']
			token = get_random_string(48)
			exp = now() + timedelta(hours=24)
			ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
			ua = request.META.get('HTTP_USER_AGENT', '')[:500]
			claim = CompanyClaim.objects.create(
				company=company,
				claimant=request.user,
				email=email,
				token=token,
				expires_at=exp,
				request_ip=(ip.split(',')[0].strip() if ip else None),
				user_agent=ua,
			)

			ActivityLog.objects.create(
				actor=request.user,
				action='company_claim_requested',
				company=company,
				details=f"Claim requested by {request.user.username} with {email}",
			)

			# Send email with verification link
			verify_url = request.build_absolute_uri(reverse('verify_claim', args=[token]))
			subject = 'Kompaniya tasdiqlash havolasi'
			body = (
				f"Salom,\n\nSiz {company.name} kompaniyasini tasdiqlash uchun so'rov yubordingiz.\n"
				f"Quyidagi havola orqali 24 soat ichida tasdiqlang:\n{verify_url}\n\nRahmat."
			)
			try:
				send_mail(subject, body, None, [email], fail_silently=True)
			except Exception:
				pass

			messages.success(request, 'Tasdiqlash havolasi email manzilingizga yuborildi.')
			return redirect('company_detail', pk=company.pk)
	else:
		form = ClaimCompanyForm(company=company)

	return render(request, 'pages/company_claim.html', {'company': company, 'form': form})


def verify_claim(request, token: str):
	try:
		claim = CompanyClaim.objects.select_related('company', 'claimant').get(token=token)
	except CompanyClaim.DoesNotExist:
		raise Http404

	if claim.status != 'pending':
		messages.info(request, 'Bu so‘rov allaqachon ko‘rib chiqilgan.')
		return redirect('company_detail', pk=claim.company.pk)

	if now() > claim.expires_at:
		claim.status = 'expired'
		claim.save(update_fields=['status'])
		messages.error(request, 'Tasdiqlash havolasi muddati tugagan.')
		return redirect('company_detail', pk=claim.company.pk)

	# Verify and assign manager
	company = claim.company
	company.manager = claim.claimant
	company.is_verified = True
	company.save(update_fields=['manager', 'is_verified'])

	claim.status = 'verified'
	claim.verified_at = now()
	claim.save(update_fields=['status', 'verified_at'])

	ActivityLog.objects.create(
		actor=claim.claimant,
		action='company_claim_verified',
		company=company,
		details=f"Claim verified for {company.name} by {claim.claimant.username}",
	)

	messages.success(request, 'Kompaniya tasdiqlandi va profilingizga biriktirildi.')
	return redirect('company_detail', pk=company.pk)


def verification_badge(request):
	return render(request, 'pages/verification_badge.html')


def privacy_policy(request):
	"""Static privacy policy page in Uzbek."""
	return render(request, 'pages/privacy_policy.html')


class PhoneForm(forms.Form):
	phone = forms.CharField(max_length=20)

	def clean_phone(self):
		import re
		raw = self.cleaned_data['phone']
		digits = re.sub(r"\D+", "", raw)
		# Allow 9-digit local (9xxxxxxxx) and normalize; or full 998xxxxxxxxx
		if len(digits) == 9:
			digits = '998' + digits
		if not (digits.startswith('998') and len(digits) == 12 and digits.isdigit()):
			raise forms.ValidationError('Telefon raqami noto‘g‘ri (998901234567).')
		return digits


def phone_signin(request):
	"""Step 1: Ask phone, send OTP using Eskiz, rate limit by phone and IP."""
	if request.method == 'POST':
		form = PhoneForm(request.POST)
		if form.is_valid():
			phone_norm = form.cleaned_data['phone']
			# cool-down: 1 OTP per 60s, max 5/hour per phone
			ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
			ip = ip.split(',')[0].strip() if ip else 'unknown'
			key_cool = f"otp_cd:{phone_norm}"
			key_hour = f"otp_hour:{phone_norm}"
			if cache.get(key_cool):
				form.add_error('phone', 'Iltimos 1 daqiqadan so‘ng urinib ko‘ring')
			else:
				sent_count = cache.get(key_hour, 0)
				if sent_count >= 5:
					form.add_error('phone', 'Ko‘p urinish. Bir soat kuting.')
				else:
					import random
					code = f"{random.randint(100000, 999999)}"
					ok = send_otp_via_eskiz(phone_norm, code)
					if not ok:
						form.add_error('phone', 'SMS yuborilmadi. Keyinroq urinib ko‘ring.')
					else:
						PhoneOTP.objects.create(phone=phone_norm, code=code)
						cache.set(key_cool, True, 60)
						cache.set(key_hour, sent_count + 1, 3600)
						request.session['phone_pending'] = phone_norm
						return redirect('phone_verify')
	else:
		form = PhoneForm()
	return render(request, 'account/phone_signin.html', {'form': form})


class VerifyForm(forms.Form):
	code = forms.CharField(max_length=6)

	def clean_code(self):
		code = (self.cleaned_data['code'] or '').strip()
		if not (len(code) == 6 and code.isdigit()):
			raise forms.ValidationError('Kod 6 xonali bo‘lishi kerak.')
		return code


def phone_verify(request):
	"""Step 2: Verify OTP and login/create user."""
	phone = request.session.get('phone_pending')
	if not phone:
		return redirect('phone_signin')
	error = None
	if request.method == 'POST':
		form = VerifyForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data['code']
			otp = PhoneOTP.objects.filter(phone=phone, is_used=False).order_by('-created_at').first()
			if not otp:
				error = 'Kod topilmadi. Qaytadan yuboring.'
			else:
				# expire after 5 minutes
				from django.utils.timezone import now
				if (now() - otp.created_at).total_seconds() > 300:
					error = 'Kod muddati tugagan.'
				else:
					if otp.code != code:
						otp.attempts += 1
						otp.save(update_fields=['attempts'])
						if otp.attempts >= 5:
							error = 'Juda ko‘p noto‘g‘ri urinish.'
						else:
							error = 'Noto‘g‘ri kod.'
					else:
						otp.is_used = True
						otp.save(update_fields=['is_used'])
						# map phone to a username scheme: u9989xxxxxxx
						username = f"u{phone}"
						user, created = User.objects.get_or_create(username=username)
						# ensure profile exists
						UserProfile.objects.get_or_create(user=user)
						login(request, user)
						request.session.pop('phone_pending', None)
						messages.success(request, 'Tizimga kirdingiz.')
						return redirect('user_profile')
	else:
		form = VerifyForm()
	return render(request, 'account/phone_verify.html', {'form': form, 'phone': phone, 'error': error})


def terms_of_service(request):
	"""Static Terms of Service page."""
	return render(request, 'pages/terms_of_service.html')


def community_guidelines(request):
	"""Static Community Guidelines page."""
	return render(request, 'pages/community_guidelines.html')


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
			if request.user.is_authenticated:
				review.user = request.user
			review.verified_purchase = True
			# New reviews require admin approval
			review.is_approved = False
			review.save()

			# Update company stats using approved reviews only
			company = review.company
			agg = company.reviews.filter(is_approved=True).aggregate(avg=Avg('rating'), cnt=Count('id'))
			company.review_count = int(agg.get('cnt') or 0)
			company.rating = round(float(agg.get('avg') or 0.0), 2) if company.review_count else 0
			company.save(update_fields=['review_count', 'rating'])

			messages.success(request, 'Sharhingiz qabul qilindi va moderator tasdiqlagandan keyin ko\'rinadi.')
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


@login_required
def manager_review_response(request, pk: int):
	"""Allow a company manager to post/edit an owner response under a review."""
	try:
		review = Review.objects.select_related('company').get(pk=pk, company__manager=request.user)
	except Review.DoesNotExist:
		raise Http404

	if request.method == 'POST':
		form = OwnerResponseForm(request.POST, instance=review)
		if form.is_valid():
			review = form.save(commit=False)
			review.owner_response_at = timezone.now()
			review.save(update_fields=['owner_response_text', 'owner_response_at'])

			# Log activity
			from .models import ActivityLog
			ActivityLog.objects.create(
				actor=request.user,
				action='owner_responded',
				company=review.company,
				review=review,
				details=f"Owner responded to review #{review.pk}",
			)

			messages.success(request, "Javob saqlandi.")
			return redirect('company_detail', pk=review.company.pk)
	else:
		form = OwnerResponseForm(instance=review)

	return render(request, 'pages/manager_review_response.html', {
		'form': form,
		'review': review,
	})
def report_review(request, pk: int):
	try:
		review = Review.objects.select_related('company').get(pk=pk)
	except Review.DoesNotExist:
		raise Http404

	# --- Rate limiting (per user/IP) ---
	def client_key():
		ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
		ip = ip.split(',')[0].strip() if ip else 'unknown'
		uid = request.user.id or 'anon'
		return f"report_rl:{uid}:{ip}"

	key = client_key()
	window_seconds = 60  # window size
	max_reports = 3      # max allowed per window
	entry = cache.get(key)
	if entry is None:
		entry = {"count": 0, "ts": now().timestamp()}
	# reset window if expired
	if now().timestamp() - entry["ts"] > window_seconds:
		entry = {"count": 0, "ts": now().timestamp()}

	if request.method == 'POST':
		# Check limit before processing
		if entry["count"] >= max_reports:
			messages.error(request, "Juda ko‘p urinish. Bir daqiqadan so‘ng qayta urinib ko‘ring.")
			return redirect('company_detail', pk=review.company.pk)

		form = ReportReviewForm(request.POST)
		if form.is_valid():
			report = form.save(commit=False)
			report.review = review
			report.reporter = request.user
			report.status = 'open'
			report.save()

			# increment counter and persist
			entry["count"] += 1
			cache.set(key, entry, timeout=window_seconds)

			# Telegram alert to admins
			reason = dict(report._meta.get_field('reason').choices).get(report.reason, report.reason)
			msg = (
				f"<b>Yangi shikoyat</b>\n"
				f"Kompaniya: {review.company.name}\n"
				f"Sharh #{review.pk} — {review.rating}⭐\n"
				f"Sabab: {reason}\n"
				f"Matn: {review.text[:200]}"
			)
			send_telegram_message(msg)

			messages.success(request, "Shikoyatingiz yuborildi. Rahmat.")
			return redirect('company_detail', pk=review.company.pk)
	else:
		form = ReportReviewForm()

	return render(request, 'pages/report_review.html', {
		'form': form,
		'review': review,
	})


def robots_txt(request):
	content = (
		"User-agent: *\n"
		"Disallow: /admin/\n"
		"Disallow: /accounts/\n"
		"Sitemap: /sitemap.xml\n"
	)
	return HttpResponse(content, content_type="text/plain")


def company_detail(request, pk: int):
	company = Company.objects.get(pk=pk)
	# Recompute assessment from stored rating/review_count which reflect only approved reviews
	company.assessment = compute_assessment(float(company.rating), int(company.review_count))
	# Base queryset: all approved reviews
	base_reviews_qs = company.reviews.filter(is_approved=True)
	reviews_qs = base_reviews_qs

	# --- Sorting & Filters ---
	sort = request.GET.get('sort', 'newest')
	with_text = request.GET.get('with_text') in ('1', 'true', 'on')
	with_response = request.GET.get('with_response') in ('1', 'true', 'on')
	# Support stars as repeated params (?stars=5&stars=4) or CSV (?stars=5,4)
	stars_list = request.GET.getlist('stars')
	if len(stars_list) == 1 and ',' in stars_list[0]:
		stars_list = [s.strip() for s in stars_list[0].split(',') if s.strip()]
	# Sanitize values to integers 1..5
	try:
		stars_selected = sorted({int(s) for s in stars_list if str(s).isdigit() and 1 <= int(s) <= 5}, reverse=True)
	except Exception:
		stars_selected = []

	if with_text:
		# "Text only" – ensure non-empty text (field is required, but keep for future)
		reviews_qs = reviews_qs.filter(~Q(text=""))

	if stars_selected:
		reviews_qs = reviews_qs.filter(rating__in=stars_selected)

	if with_response:
		reviews_qs = reviews_qs.exclude(owner_response_text="")

	if sort == 'highest':
		reviews_qs = reviews_qs.order_by('-rating', '-created_at')
	elif sort == 'lowest':
		reviews_qs = reviews_qs.order_by('rating', '-created_at')
	else:  # newest (default)
		reviews_qs = reviews_qs.order_by('-created_at')
	# Rating distribution counts per star (1..5) from all approved reviews (unfiltered)
	dist_counts = {i: 0 for i in range(1, 6)}
	agg = base_reviews_qs.values('rating').annotate(c=Count('id'))
	for row in agg:
		r = int(row['rating'])
		if 1 <= r <= 5:
			dist_counts[r] = int(row['c'])
	total = sum(dist_counts.values()) or 1
	dist = []
	for star in range(5, 1 - 1, -1):
		count = dist_counts.get(star, 0)
		pct = round((count / total) * 100)
		dist.append({'star': star, 'count': count, 'percent': pct})

	# --- Pagination ---
	paginator = Paginator(reviews_qs, 10)
	page_obj = paginator.get_page(request.GET.get('page'))

	# Preserve query params (except page) for pagination links
	qd = request.GET.copy()
	qd.pop('page', None)
	qs_base = qd.urlencode()
	if qs_base:
		qs_base = qs_base + '&'

	# QS for clickable bars without stars
	qd_no_stars = request.GET.copy()
	for k in ['page', 'stars']:
		qd_no_stars.pop(k, None)
	qs_no_stars = qd_no_stars.urlencode()
	if qs_no_stars:
		qs_no_stars = qs_no_stars + '&'

	reviews = page_obj.object_list
	# numeric pagination window
	current = page_obj.number
	total_pages = paginator.num_pages
	window = 2
	start = max(1, current - window)
	end = min(total_pages, current + window)
	pages_to_show = list(range(start, end + 1))

	filters_active = bool(with_text or with_response or stars_selected)
	qd_clear = request.GET.copy()
	for k in ['with_text', 'with_response', 'stars', 'page']:
		qd_clear.pop(k, None)
	clear_filters_qs = qd_clear.urlencode()

	years_on_site = max(0, int((timezone.now() - company.created_at).days // 365))
	# Map URL (no geocode dependency): prefer lat/lng else search by address
	if company.lat and company.lng:
		map_url = f"https://www.google.com/maps/search/?api=1&query={company.lat},{company.lng}"
	elif company.address:
		from urllib.parse import quote
		q = quote(f"{company.address} {company.city}")
		map_url = f"https://www.google.com/maps/search/?api=1&query={q}"
	else:
		map_url = ''

	# Determine if current user liked this company
	liked_state = False
	if request.user.is_authenticated:
		liked_state = CompanyLike.objects.filter(company=company, user=request.user).exists()

	return render(request, 'pages/company_detail.html', {
		'company': company,
		'reviews': reviews,
		'rating_distribution': dist,
		# pagination & controls
		'page_obj': page_obj,
		'paginator': paginator,
		'current_sort': sort,
		'with_text': with_text,
		'with_response': with_response,
		'current_stars': stars_selected,
		'qs_base': qs_base,
		'star_options': [5, 4, 3, 2, 1],
		'qs_no_stars': qs_no_stars,
		'pages_to_show': pages_to_show,
		'filters_active': filters_active,
		'clear_filters_qs': clear_filters_qs,
		'years_on_site': years_on_site,
	'map_url': map_url,
	'liked_state': liked_state,
	})


@login_required
def reveal_contact(request, pk: int, kind: str):
	"""Reveal phone or email; increments counters and logs activity."""
	try:
		company = Company.objects.get(pk=pk)
	except Company.DoesNotExist:
		raise Http404
	if kind not in ('phone', 'email'):
		return JsonResponse({'ok': False, 'error': 'invalid'}, status=400)
	value = company.phone_public if kind == 'phone' else company.email_public
	if not value:
		return JsonResponse({'ok': False, 'error': 'not_set'}, status=404)
	ActivityLog.objects.create(
		actor=request.user,
		action='contact_revealed',
		company=company,
		details=f"{kind} revealed",
	)
	return JsonResponse({'ok': True, 'value': value})


@login_required
def like_company(request, pk: int):
	try:
		company = Company.objects.get(pk=pk)
	except Company.DoesNotExist:
		raise Http404
	# Toggle like per user using CompanyLike
	liked = False
	obj, created = CompanyLike.objects.get_or_create(company=company, user=request.user)
	if created:
		liked = True
		# increment cached counter
		from django.db.models import F
		Company.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
		ActivityLog.objects.create(actor=request.user, action='company_liked', company=company, details="liked")
	else:
		# already liked → unlike
		obj.delete()
		from django.db.models import F
		Company.objects.filter(pk=pk, like_count__gt=0).update(like_count=F('like_count') - 1)
		ActivityLog.objects.create(actor=request.user, action='company_liked', company=company, details="unliked")

	current = Company.objects.filter(pk=pk).values_list('like_count', flat=True).first()
	return JsonResponse({'ok': True, 'like_count': int(current or 0), 'liked': liked})


@login_required
def user_profile(request):
	# Ensure profile exists
	profile, _ = UserProfile.objects.get_or_create(user=request.user)

	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save()
			return redirect('user_profile')
	else:
		form = ProfileForm(instance=profile)

	# Pull user's reviews (owned via FK or fallback by user_name match)
	user_reviews = Review.objects.filter(Q(user=request.user) | Q(user_name=request.user.username)).select_related('company')

	# Compute real stats for header
	from django.db.models import Avg, Count
	stats = user_reviews.aggregate(
		avg_rating=Avg('rating'),
		total_reviews=Count('id'),
	)
	total_reviews = int(stats.get('total_reviews') or 0)
	avg_rating = float(stats.get('avg_rating') or 0.0)
	unique_companies = user_reviews.values('company').distinct().count()
	helpful_votes = 0  # Placeholder until a like/upvote model exists

	return render(request, 'pages/user_profile.html', {
		'form': form,
		'user_reviews': user_reviews,
		'profile': profile,
		'profile_stats': {
			'total_reviews': total_reviews,
			'avg_rating': avg_rating,
			'unique_companies': unique_companies,
			'helpful_votes': helpful_votes,
		},
	})


@login_required
def review_edit(request, pk: int):
	try:
		review = Review.objects.get(pk=pk)
	except Review.DoesNotExist:
		raise Http404

	if review.user_id != request.user.id:
		raise Http404

	if request.method == 'POST':
		form = ReviewEditForm(request.POST, instance=review)
		if form.is_valid():
			form.save()
			messages.success(request, 'Sharh yangilandi.')
			return redirect('user_profile')
	else:
		form = ReviewEditForm(instance=review)

	return render(request, 'pages/review_edit.html', {'form': form, 'review': review})


@login_required
def review_delete(request, pk: int):
	try:
		review = Review.objects.get(pk=pk)
	except Review.DoesNotExist:
		raise Http404

	if review.user_id != request.user.id:
		raise Http404

	if request.method == 'POST':
		review.delete()
		messages.success(request, 'Sharh o\'chirildi.')
		return redirect('user_profile')

	return render(request, 'pages/review_delete_confirm.html', {'review': review})