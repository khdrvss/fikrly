from django.core.management.base import BaseCommand
from django.db import transaction

from frontend.models import BusinessCategory, Company


class Command(BaseCommand):
    help = "Populate translation fields (copy existing default language content into *_uz fields)"

    def handle(self, *args, **options):
        self.stdout.write("Populating translation fields for BusinessCategory and Company...")
        with transaction.atomic():
            # Categories
            cats = BusinessCategory.objects.all()
            for c in cats:
                updated = False
                if hasattr(c, 'name_uz') and (not getattr(c, 'name_uz')):
                    c.name_uz = c.name
                    updated = True
                if updated:
                    c.save()

            # Companies
            comps = Company.objects.all()
            for comp in comps:
                updated = False
                if hasattr(comp, 'name_uz') and (not getattr(comp, 'name_uz')):
                    comp.name_uz = comp.name
                    updated = True
                if hasattr(comp, 'description_uz') and (not getattr(comp, 'description_uz')):
                    comp.description_uz = comp.description
                    updated = True
                if updated:
                    comp.save()

        self.stdout.write(self.style.SUCCESS("Translation fields populated (where present)."))
