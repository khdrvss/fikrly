from django.core.management.base import BaseCommand
from frontend.models import BusinessCategory, Company, Review

COMPANIES = [
    {
        "name": "UzAuto Motors",
        "category": "Avto kompaniyalar",
        "city": "Asaka",
        "description": "O'zbekistondagi eng yirik avtomobil ishlab chiqaruvchisi.",
        "image_url": "https://images.unsplash.com/photo-1588698943314-e5e3b5a45b7f?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.6,
    },
    {
        "name": "Coca-Cola Uzbekistan",
        "category": "Ichimliklar",
        "city": "Toshkent",
        "description": "Coca-Cola kompaniyasining O'zbekistondagi filiali.",
        "image_url": "https://images.unsplash.com/photo-1543168256-418292c2b740?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.5,
    },
    {
        "name": "Uzbekneftegaz",
        "category": "Oil and Gas",
        "city": "Toshkent",
        "description": "Davlat neft-gaz kompaniyasi.",
        "image_url": "https://images.unsplash.com/photo-1616401036329-873d6f4d22c3?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.2,
    },
    {
        "name": "Uztelecom",
        "category": "Telecommunications",
        "city": "Toshkent",
        "description": "Yirik telekommunikatsiya operatori.",
        "image_url": "https://images.unsplash.com/photo-1585097479429-c8c3605e5482?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.0,
    },
    {
        "name": "Ucell",
        "category": "Mobile Operator",
        "city": "Toshkent",
        "description": "Mobil aloqa operatori.",
        "image_url": "https://images.unsplash.com/photo-1520111531278-65b1c9c4c2a5?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.1,
    },
    {
        "name": "Beeline Uzbekistan",
        "category": "Mobile Operator",
        "city": "Toshkent",
        "description": "Mashhur mobil aloqa operatori.",
        "image_url": "https://images.unsplash.com/photo-1527712169527-dfd63507204f?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.3,
    },
    {
        "name": "EVOS",
        "category": "Fast-food",
        "city": "Toshkent",
        "description": "Fast-food tarmog'i.",
        "image_url": "https://images.unsplash.com/photo-1563852089201-4475518b29c9?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.5,
    },
    {
        "name": "Les Ailes",
        "category": "Fast-food",
        "city": "Toshkent",
        "description": "Tovuq taomlari bilan mashhur.",
        "image_url": "https://images.unsplash.com/photo-1563852089201-4475518b29c9?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.4,
    },
    {
        "name": "Korzinka",
        "category": "Supermarket",
        "city": "Toshkent",
        "description": "Chakana savdo tarmog'i.",
        "image_url": "https://images.unsplash.com/photo-1542838177-d5d4d3d4b6c3?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.6,
    },
    {
        "name": "TBC Bank Uzbekistan",
        "category": "Bank",
        "city": "Toshkent",
        "description": "Raqamli bank.",
        "image_url": "https://images.unsplash.com/photo-1560518712-421b8c199589?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.4,
    },
    {
        "name": "SOLIDEX",
        "category": "Qurilish",
        "city": "Toshkent",
        "description": "2024-2025 yillarda O'zbekistonda eng yaxshi ish beruvchi kompaniyalar qatoriga kirgan qurilish kompaniyasi.",
        "image_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "DISCOVER INVEST",
        "category": "Qurilish",
        "city": "Toshkent",
        "description": "O'zbekistondagi yetakchi qurilish kompaniyalaridan biri bo'lib, eng yaxshi ish beruvchilar reytingida yuqori o'rinlarni egallagan.",
        "image_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "ANGLESEY FOOD",
        "category": "Chakana savdo",
        "city": "Toshkent",
        "description": "Korzinka supermarketlar tarmog'iga egalik qiluvchi kompaniya. Eng ko'p ish beruvchi korxonalar qatorida e'tirof etilgan.",
        "image_url": "https://images.unsplash.com/photo-1542838177-d5d4d3d4b6c3?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "CALIK ENERJI SAN. VE TIC. A.S.",
        "category": "Energetika",
        "city": "Turli shaharlar",
        "description": "Turkiyaning energetika sohasidagi yirik kompaniyasi. O'zbekistonda yangi loyihalarni amalga oshirmoqda.",
        "image_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "Zarafshon industrial technology",
        "category": "Kimyo sanoati",
        "city": "Karmana",
        "description": "Xitoy sarmoyasi ishtirokidagi qo'shma korxona. Kaustik soda va xlor mahsulotlari ishlab chiqarish loyihasini boshlagan.",
        "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "Metal processing technology (ICG)",
        "category": "Metallurgiya",
        "city": "Ohangaron",
        "description": "Qiymati 20 million dollarlik ishlab chiqarishni kengaytirish loyihasi doirasida mis quvurlari va fitinglar ishlab chiqarishni yo'lga qo'ygan.",
        "image_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "BYD Uzbekistan Factory",
        "category": "Avto kompaniyalar",
        "city": "Turli shaharlar",
        "description": "Xitoyning BYD kompaniyasi bilan hamkorlikda O'zbekistonda elektromobillar ishlab chiqarishni yo'lga qo'ygan yangi zavod.",
        "image_url": "https://images.unsplash.com/photo-1588698943314-e5e3b5a45b7f?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "ADM Jizzakh",
        "category": "Avto kompaniyalar",
        "city": "Jizzax",
        "description": "Jizzax viloyatida joylashgan avtomobil zavodi. Chevrolet va Isuzu brendlari ostida avtomobillar va yuk mashinalari yig'ish bilan shug'ullanadi.",
        "image_url": "https://images.unsplash.com/photo-1588698943314-e5e3b5a45b7f?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "My Freighter",
        "category": "Aviatsiya",
        "city": "Toshkent",
        "description": "Xalqaro yuk tashishga ixtisoslashgan mahalliy aviakompaniya. Yuk havo qatnovlarini amalga oshiradi.",
        "image_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Octobank",
        "category": "Bank",
        "city": "Toshkent",
        "description": "Raqamli banking xizmatlarini taqdim etuvchi yangi bank. Innovatsion fintech yechimlarini joriy etishga e'tibor qaratadi.",
        "image_url": "https://images.unsplash.com/photo-1560518712-421b8c199589?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Yandex Lavka",
        "category": "Oziq-ovqat yetkazib berish",
        "city": "Toshkent",
        "description": "Yandex tomonidan ishga tushirilgan, tezkor oziq-ovqat yetkazib berish xizmati. Darkstorlar orqali buyurtmalarni amalga oshiradi.",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Agalarov Development",
        "category": "Ko'chmas mulk",
        "city": "Toshkent",
        "description": "Ozarbayjonning yirik ko'chmas mulk kompaniyasi. Toshkentda premium turar-joy majmuasi qurishni rejalashtirmoqda.",
        "image_url": "https://images.unsplash.com/photo-1560518712-421b8c199589?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "Ariya Teks",
        "category": "To'qimachilik",
        "city": "Toshkent",
        "description": "Yevropa bozoriga chiqishni rejalashtirgan to'qimachilik kompaniyasi. Amazon va Shopify kabi platformalar bilan hamkorlik qilmoqda.",
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "DM Paper",
        "category": "Qurilish materiallari",
        "city": "Samarqand",
        "description": "Gipsokarton uchun qog'oz ishlab chiqaradigan yangi kompaniya. Qozog'iston, Turkmaniston va Ozarbayjon bozorlariga eksportni boshlagan.",
        "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "Asaxiy Books",
        "category": "Elektronika, E-commerce",
        "city": "Toshkent",
        "description": "O'zbekistondagi eng yirik onlayn do'konlardan biri. Kitoblar, elektronika va boshqa mahsulotlarni sotadi.",
        "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.8,
    },
    {
        "name": "Express24",
        "category": "Oziq-ovqat yetkazib berish",
        "city": "Toshkent",
        "description": "Toshkentdagi yetakchi oziq-ovqat va taom yetkazib berish xizmatlaridan biri. Ko'plab restoranlar bilan hamkorlik qiladi.",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.5,
    },
    {
        "name": "Payme",
        "category": "Fintech",
        "city": "Toshkent",
        "description": "O'zbekistondagi eng mashhur mobil to'lov ilovalaridan biri. Kommunal to'lovlar, mobil aloqa va boshqa xizmatlar uchun to'lovlarni amalga oshirish imkonini beradi.",
        "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.7,
    },
    {
        "name": "Click",
        "category": "Fintech",
        "city": "Toshkent",
        "description": "Mobil to'lov tizimi. Foydalanuvchilarga UzCard va HUMO kartalari orqali xizmatlar uchun to'lovlarni amalga oshirishni taklif qiladi.",
        "image_url": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.6,
    },
    {
        "name": "IT Park Uzbekistan",
        "category": "IT, Texnologiya",
        "city": "Toshkent",
        "description": "IT-kompaniyalar va startaplar uchun maxsus texnologiya parki. Rezident kompaniyalarga soliq imtiyozlari va infratuzilma yordami beradi.",
        "image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 5.0,
    },
    {
        "name": "Zamin Fondi",
        "category": "Nodavlat notijorat tashkiloti",
        "city": "Toshkent",
        "description": "Ekologiya, atrof-muhitni muhofaza qilish va ijtimoiy loyihalarni qo'llab-quvvatlash bilan shug'ullanuvchi fond.",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Green White Solutions",
        "category": "IT",
        "city": "Toshkent",
        "description": "Dasturiy ta'minot ishlab chiqish, veb-dizayn va IT-konsalting xizmatlarini taklif etuvchi kompaniya.",
        "image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.9,
    },
    {
        "name": "Huawei Uzbekistan",
        "category": "Telekommunikatsiya",
        "city": "Toshkent",
        "description": "Xalqaro Huawei kompaniyasining O'zbekistondagi filiali. Telekommunikatsiya uskunalarini o'rnatish va texnik xizmat ko'rsatish bilan shug'ullanadi.",
        "image_url": "https://images.unsplash.com/photo-1585097479429-c8c3605e5482?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.5,
    },
    {
        "name": "BMB Trade Group",
        "category": "Eksport, logistika",
        "city": "Toshkent",
        "description": "O'zbekistondagi yirik eksport-import kompaniyasi. Qishloq xo'jaligi mahsulotlarini yetishtirish va eksport qilish bilan shug'ullanadi.",
        "image_url": "https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Toshkent Yuz",
        "category": "Oziq-ovqat ishlab chiqarish",
        "city": "Toshkent",
        "description": "Yangi taomlar ishlab chiqarish va sotishga yo'naltirilgan oziq-ovqat kompaniyasi. Mahalliy bozorga yangi mahsulotlar bilan kirib kelmoqda.",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
    {
        "name": "G'oliblar KDB",
        "category": "Qurilish materiallari",
        "city": "Toshkent",
        "description": "Zamonaviy qurilish materiallari, xususan, energiya tejovchi bloklar va g'ishtlar ishlab chiqarishni yo'lga qo'ygan yangi korxona.",
        "image_url": "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": None,
    },
    {
        "name": "Digital Chain",
        "category": "IT, Raqamli marketing",
        "city": "Toshkent",
        "description": "Raqamli marketing, veb-sayt yaratish va mobil ilovalar ishlab chiqarishga ixtisoslashgan IT-kompaniya.",
        "image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.8,
    },
    {
        "name": "Proxima Solutions",
        "category": "IT, Konsalting",
        "city": "Toshkent",
        "description": "Biznes uchun axborot texnologiyalari yechimlarini taklif qiluvchi kompaniya. Loyiha boshqaruvi va texnik xizmat ko'rsatish bilan shug'ullanadi.",
        "image_url": "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?q=80&w=1200&auto=format&fit=crop",
        "is_verified": True,
        "rating": 4.9,
    },
    {
        "name": "Mironshoh Teks",
        "category": "To'qimachilik",
        "city": "Toshkent viloyati",
        "description": "Paxta tolasini qayta ishlash va ip-kalava ishlab chiqarishga ixtisoslashgan yangi to'qimachilik korxonasi.",
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?q=80&w=1200&auto=format&fit=crop",
        "is_verified": False,
        "rating": None,
    },
]

DEFAULT_REVIEW_TEXTS = [
    "Xizmat sifati yaxshi, tavsiya qilaman.",
    "Narxlar mos, yana kelaman.",
    "Juda ham yoqdi, xodimlar xushmuomala.",
]


class Command(BaseCommand):
    help = "Seed database with Uzbek companies and ensure at least one review for each."

    def handle(self, *args, **options):
        Review.objects.all().delete()
        Company.objects.all().delete()

        # Flatten any nested lists inside COMPANIES
        flat_companies = []
        for entry in COMPANIES:
            if isinstance(entry, dict):
                flat_companies.append(entry)
            elif isinstance(entry, list):
                flat_companies.extend([e for e in entry if isinstance(e, dict)])

        total_reviews = 0
        for payload in flat_companies:
            # Extract rating hint robustly
            raw_rating = payload.pop("rating", None)
            try:
                rating_hint = float(raw_rating) if raw_rating is not None else 4.0
            except Exception:
                rating_hint = 4.0

            # Resolve category string to BusinessCategory FK
            category_name = payload.pop("category", None)
            if category_name:
                cat_obj, _ = BusinessCategory.objects.get_or_create(
                    name=category_name,
                    defaults={"slug": category_name.lower().replace(" ", "-").replace(",", "")[:60]},
                )
                payload["category_fk"] = cat_obj

            # Ensure optional fields exist
            payload.setdefault("image_url", "")
            payload.setdefault("description", "")
            payload.setdefault("city", "")
            payload.setdefault("is_verified", False)

            company = Company.objects.create(**payload)

            # Always at least one review
            seed_rating = max(1, min(5, int(round(rating_hint))))
            Review.objects.create(
                company=company,
                user_name="Foydalanuvchi",
                rating=seed_rating,
                text=DEFAULT_REVIEW_TEXTS[0],
                verified_purchase=True,
            )
            total_reviews += 1

            # Add a second review for higher-rated brands
            if rating_hint >= 4.5:
                Review.objects.create(
                    company=company,
                    user_name="Mehmon",
                    rating=5,
                    text=DEFAULT_REVIEW_TEXTS[1],
                    verified_purchase=True,
                )
                total_reviews += 1

            # Update denormalized fields
            company.review_count = company.reviews.count()
            company.rating = round(
                sum(r.rating for r in company.reviews.all()) / company.review_count, 2
            )
            company.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Company.objects.count()} companies and {total_reviews} reviews."
            )
        )
