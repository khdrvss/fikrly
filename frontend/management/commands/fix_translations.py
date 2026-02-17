from django.core.management.base import BaseCommand
from frontend.models import Company, BusinessCategory


class Command(BaseCommand):
    help = "Populate translation fields with existing data"

    def handle(self, *args, **options):
        models = [Company, BusinessCategory]

        for model in models:
            self.stdout.write(f"Processing {model.__name__}...")

            qs = model.objects.all()
            total = qs.count()
            self.stdout.write(f" Found {total} objects")

            for obj in qs.iterator():
                changed_fields = []

                # name -> name_uz / name_ru
                if hasattr(obj, "name"):
                    if hasattr(obj, "name_uz") and not getattr(obj, "name_uz"):
                        setattr(obj, "name_uz", getattr(obj, "name"))
                        changed_fields.append("name_uz")
                    if hasattr(obj, "name_ru") and not getattr(obj, "name_ru"):
                        setattr(obj, "name_ru", getattr(obj, "name"))
                        changed_fields.append("name_ru")

                # description -> description_uz / description_ru
                if hasattr(obj, "description"):
                    if hasattr(obj, "description_uz") and not getattr(
                        obj, "description_uz"
                    ):
                        setattr(obj, "description_uz", getattr(obj, "description"))
                        changed_fields.append("description_uz")
                    if hasattr(obj, "description_ru") and not getattr(
                        obj, "description_ru"
                    ):
                        setattr(obj, "description_ru", getattr(obj, "description"))
                        changed_fields.append("description_ru")

                if changed_fields:
                    try:
                        obj.save(update_fields=changed_fields)
                    except Exception:
                        # fallback to full save if partial update fails for any reason
                        obj.save()

        self.stdout.write(
            self.style.SUCCESS("Translation fields populated successfully.")
        )
