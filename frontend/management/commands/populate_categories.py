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
        
        # Icon and color mapping
        if any(word in name_lower for word in ['restoran', 'kafe', 'fast-food', 'ovqat']):
            return '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>', 'red'
        elif any(word in name_lower for word in ['bank', 'moliya', 'fintech']):
            return '<path d="M12 2L3 7V8H21V7L12 2Z"/><path d="M4 9V19H20V9"/><path d="M8 15V13H10V15H8Z"/><path d="M14 15V13H16V15H14Z"/>', 'blue'
        elif any(word in name_lower for word in ['it', 'texnologiya', 'dasturlash', 'konsalting', 'raqamli']):
            return '<path d="M9 12L11 14L15 10"/><path d="M21 12C21 16.97 16.97 21 12 21S3 16.97 3 12S7.03 3 12 3S21 7.03 21 12Z"/>', 'purple'
        elif any(word in name_lower for word in ['tibbiyot', 'klinika', 'dorixona', 'health']):
            return '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>', 'green'
        elif any(word in name_lower for word in ['ta\'lim', 'maktab', 'universitet', 'kurs']):
            return '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>', 'orange'
        elif any(word in name_lower for word in ['savdo', 'do\'kon', 'supermarket', 'chakana', 'commerce']):
            return '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/>', 'yellow'
        elif any(word in name_lower for word in ['avtomobil', 'automotive', 'transport']):
            return '<path d="M7 17a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/><path d="M17 17a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"/><path d="M5 17H3s-1-9 1-11h16s2 2 1 11h-2"/>', 'gray'
        elif any(word in name_lower for word in ['qurilish', 'construction', 'materiallari']):
            return '<path d="M10 20V14H14V20H19V12H22L12 3L2 12H5V20H10Z"/>', 'orange'
        elif any(word in name_lower for word in ['telekommunikatsiya', 'operator', 'mobile']):
            return '<path d="M22 16.92V19.92C22 20.51 21.39 21 20.92 21C18.95 20.87 16.95 20.22 15.21 19.27C13.15 18.15 11.26 16.26 10.14 14.2C9.19 12.46 8.54 10.46 8.41 8.49C8.4 8.18 8.56 7.65 9.01 7.65H12.01"/>', 'blue'
        elif any(word in name_lower for word in ['energetika', 'energy', 'electricity']):
            return '<path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/>', 'yellow'
        elif any(word in name_lower for word in ['to\'qimachilik', 'textile', 'fashion']):
            return '<path d="M12 2L2 7L12 12L22 7L12 2Z"/><path d="M2 17L12 22L22 17"/><path d="M2 12L12 17L22 12"/>', 'pink'
        elif any(word in name_lower for word in ['metallurgiya', 'metal', 'mining', 'konchilik']):
            return '<path d="M9 11H15L13 13L15 15H9L11 13L9 11Z"/><path d="M12 2L22 8.5V15.5L12 22L2 15.5V8.5L12 2Z"/>', 'gray'
        elif any(word in name_lower for word in ['aviatsiya', 'aviation', 'aircraft']):
            return '<path d="M21 16V4.58C21 4.21 20.81 3.85 20.49 3.62C20.17 3.38 19.73 3.28 19.3 3.34L3.3 5.35C2.67 5.44 2.25 6.03 2.25 6.7V16"/>', 'blue'
        elif any(word in name_lower for word in ['beverage', 'ichimlik', 'drink']):
            return '<path d="M5 12V7L7 5H17L19 7V12"/><path d="M5 12L2 22H22L19 12"/>', 'green'
        elif any(word in name_lower for word in ['kimyo', 'chemical', 'sanoati']):
            return '<path d="M10.5 2L8.5 8H15.5L13.5 2H10.5Z"/><path d="M7 8L5 16C4.72 17.2 5.54 18.36 6.76 18.64L17.24 18.64C18.46 18.36 19.28 17.2 19 16L17 8H7Z"/>', 'purple'
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
