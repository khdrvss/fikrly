from django.core.management.base import BaseCommand
from django.utils.text import slugify
from frontend.models import Category, Company


class Command(BaseCommand):
    help = 'Populate all categories from company data with icons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-companies',
            action='store_true',
            help='Create categories from all company categories in database',
        )

    def get_category_icon_and_color(self, name):
        """Return appropriate icon and color based on category name"""
        name_lower = name.lower()

        # Simple stroke-based icons (the original working style)
        if any(word in name_lower for word in ['restoran', 'kafe', 'fast-food', 'ovqat']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>', 'red'
        elif any(word in name_lower for word in ['bank', 'moliya', 'fintech']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>', 'blue'
        elif any(word in name_lower for word in ['it', 'texnologiya', 'dasturlash', 'konsalting', 'raqamli']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>', 'purple'
        elif any(word in name_lower for word in ['tibbiyot', 'klinika', 'dorixona', 'health']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>', 'green'
        elif any(word in name_lower for word in ['ta\'lim', 'maktab', 'universitet', 'kurs']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>', 'orange'
        elif any(word in name_lower for word in ['savdo', 'do\'kon', 'supermarket', 'chakana', 'commerce', 'elektronika']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>', 'yellow'
        elif any(word in name_lower for word in ['avtomobil', 'automotive', 'transport', 'avto']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>', 'gray'
        elif any(word in name_lower for word in ['qurilish', 'construction', 'materiallari']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>', 'orange'
        elif any(word in name_lower for word in ['telekommunikatsiya', 'operator', 'mobile']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/>', 'blue'
        elif any(word in name_lower for word in ['energetika', 'energy', 'electricity']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>', 'yellow'
        elif any(word in name_lower for word in ['to\'qimachilik', 'textile', 'fashion']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"/>', 'pink'
        elif any(word in name_lower for word in ['metallurgiya', 'metal', 'mining', 'konchilik']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>', 'gray'
        elif any(word in name_lower for word in ['aviatsiya', 'aviation', 'aircraft']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>', 'blue'
        elif any(word in name_lower for word in ['beverage', 'ichimlik', 'drink']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v6a2 2 0 002 2h2m2-2V9a2 2 0 012-2h2a2 2 0 012 2v.01M15 8v.01"/>', 'green'
        elif any(word in name_lower for word in ['kimyo', 'chemical', 'sanoati']):
            return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/>', 'purple'
        elif any(word in name_lower for word in ['mulk', 'real estate', 'property']):
            return '<path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z"/>', 'green'
        elif any(word in name_lower for word in ['logistika', 'yetkazib', 'delivery', 'eksport']):
            return '<path d="M14 18V6C14 5.45 13.55 5 13 5H11C10.45 5 10 5.45 10 6V18L7 21L12 19L17 21L14 18Z"/>', 'orange'
        elif any(word in name_lower for word in ['oil', 'gas', 'neft']):
            return '<path d="M9 2V13C9 14.1 9.9 15 11 15H13C14.1 15 15 14.1 15 13V2H9Z"/><path d="M12 15V22"/>', 'gray'
        elif any(word in name_lower for word in ['test', 'sinov']):
            return '<path d="M14 2H6C4.9 2 4.01 2.9 4.01 4L4 20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>', 'gray'
        else:
            # Default icon and color
            return '<path d="M12 2L2 7L12 12L22 7L12 2Z"/><path d="M2 17L12 22L22 17"/><path d="M2 12L12 17L22 12"/>', 'gray'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        if options['from_companies']:
            self.stdout.write('Creating categories from company data...')

            # Get all unique categories from companies
            company_categories = Company.objects.values_list('category', flat=True).distinct()
            company_categories = [cat for cat in company_categories if cat and cat.strip()]

            for i, cat_name in enumerate(sorted(company_categories), 1):
                icon_svg, color = self.get_category_icon_and_color(cat_name)
                slug = slugify(cat_name)

                category_data = {
                    'slug': slug,
                    'description': f'{cat_name} sohasidagi kompaniyalar',
                    'icon_svg': icon_svg,
                    'color': color,
                    'sort_order': i * 10,
                    'is_active': True
                }

                category, created = Category.objects.get_or_create(
                    name=cat_name,
                    defaults=category_data
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Yaratildi: {category.name} ({color})')
                    )
                else:
                    # Update existing category if needed
                    updated = False
                    for key, value in category_data.items():
                        if getattr(category, key) != value:
                            setattr(category, key, value)
                            updated = True

                    if updated:
                        category.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'↻ Yangilandi: {category.name}')
                        )

        else:
            # Original manual categories data
            categories_data = [
                {
                    'name': 'Restoran va Kafe',
                    'slug': 'restoran-va-kafe',
                    'description': 'Ovqatlanish joylari, restoranlar, kafeler va boshqa oziq-ovqat xizmatlari',
                    'icon_svg': '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
                    'color': 'red',
                    'sort_order': 10
                },
                {
                    'name': 'Bank',
                    'slug': 'bank',
                    'description': 'Bank xizmatlari, moliya institutlari',
                    'icon_svg': '<path d="M12 2L3 7V8H21V7L12 2Z"/><path d="M4 9V19H20V9"/><path d="M8 15V13H10V15H8Z"/><path d="M14 15V13H16V15H14Z"/>',
                    'color': 'blue',
                    'sort_order': 20
                }
            ]

            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults=cat_data
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Yaratildi: {category.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Yakunlandi: {created_count} ta yaratildi, {updated_count} ta yangilandi'
            )
        )
