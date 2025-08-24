from django.core.management.base import BaseCommand
from frontend.models import Company, Review


COMPANIES = [
    {
        "name": "Oqtepa Lavash",
        "category": "Restaurant",
        "city": "Toshkent",
        "description": "O'zbekistondagi mashhur fast food tarmog'i.",
        "is_verified": True,
        "rating": 4.8,
        "reviews": [
            ("Aziza Karimova", 5, "Lavash juda mazali, xizmat tez va xodimlar mehribon."),
            ("Bobur Rahimov", 4, "Taomlar yaxshi, ba'zan gavjum bo'ladi."),
        ],
    },
    {
        "name": "Bellissimo Pizza",
        "category": "Restaurant",
        "city": "Toshkent",
        "description": "Oilaviy pitsa tarmog'i, tez yetkazib berish xizmati.",
        "is_verified": True,
        "rating": 4.6,
        "reviews": [
            ("Malika Tosheva", 5, "Pitsa doim issiq va mazali keladi, yetkazib berish tez."),
            ("Javlon Rustamov", 4, "Narxlar mos, garnir biroz yaxshilansa yaxshi bo'lardi."),
        ],
    },
    {
        "name": "UZUM Market",
        "category": "E-commerce",
        "city": "Toshkent",
        "description": "Onlayn marketplace - tez yetkazib berish va kafolat.",
        "is_verified": True,
        "rating": 4.5,
        "reviews": [
            ("Sardor Bek", 5, "Buyurtmalar tez keladi, qaytarish jarayoni ham oson."),
            ("Nigora M.", 4, "Assortiment keng, ba'zi tovarlar kechikadi."),
        ],
    },
    {
        "name": "Artel",
        "category": "Electronics",
        "city": "Toshkent",
        "description": "Maishiy texnika ishlab chiqaruvchisi.",
        "is_verified": True,
        "rating": 4.4,
        "reviews": [
            ("Akmal Qodirov", 5, "Muzlatkich juda jim ishlaydi, elektr tejaydi."),
            ("Shahnoza", 4, "Kafolat xizmati yaxshi, ustalar tez keldi."),
        ],
    },
    {
        "name": "HUMO Bank",
        "category": "Bank",
        "city": "Toshkent",
        "description": "Raqamli bank xizmatlari va qulay mobil ilova.",
        "is_verified": True,
        "rating": 4.3,
        "reviews": [
            ("Dilshod", 5, "Ilovasi tez, kartadan kartaga o'tkazma qulay."),
            ("Mavluda", 4, "Navbatlar bor edi, lekin operatorlar yordam berdi."),
        ],
    },
    {
        "name": "Beeline Uzbekistan",
        "category": "Telecom",
        "city": "Toshkent",
        "description": "Mobil aloqa operatori, keng qamrovli internet.",
        "is_verified": True,
        "rating": 4.1,
        "reviews": [
            ("Jasur", 4, "Internet tezligi yaxshi, ba'zi hududlarda pasayadi."),
            ("Lola", 4, "Tariflar o'zgarib turadi, lekin xizmat barqaror."),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed database with major Uzbek companies and realistic reviews."

    def handle(self, *args, **options):
        created_total = 0
        Review.objects.all().delete()
        Company.objects.all().delete()

        for payload in COMPANIES:
            reviews = payload.pop("reviews", [])
            company, _ = Company.objects.get_or_create(name=payload["name"], defaults=payload)
            # If company existed, update fields
            for k, v in payload.items():
                setattr(company, k, v)
            company.save()

            for user_name, rating, text in reviews:
                Review.objects.create(
                    company=company,
                    user_name=user_name,
                    rating=rating,
                    text=text,
                    verified_purchase=True,
                )
                created_total += 1

            # Update denormalized counters
            company.review_count = company.reviews.count()
            if company.review_count:
                company.rating = round(
                    sum(r.rating for r in company.reviews.all()) / company.review_count, 2
                )
            company.save()

        self.stdout.write(self.style.SUCCESS(f"Seeded {Company.objects.count()} companies and {created_total} reviews."))


