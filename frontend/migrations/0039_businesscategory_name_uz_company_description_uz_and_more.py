"""Generated migration to add translated fields and image variants.

This migration adds nullable translation columns first, populates them
from existing values, and keeps them nullable to avoid NOT NULL issues
during the rollout. Later migrations can tighten constraints if desired.
"""

from django.db import migrations, models


def populate_translations(apps, schema_editor):
    BusinessCategory = apps.get_model("frontend", "BusinessCategory")
    Company = apps.get_model("frontend", "Company")
    from django.db.models import F

    # Category name
    BusinessCategory.objects.filter(name_ru="").update(name_ru=F("name"))
    BusinessCategory.objects.filter(name_ru__isnull=True).update(name_ru=F("name"))

    # Company name
    Company.objects.filter(name_ru="").update(name_ru=F("name"))
    Company.objects.filter(name_ru__isnull=True).update(name_ru=F("name"))

    # Company description
    Company.objects.filter(description_ru="").update(description_ru=F("description"))
    Company.objects.filter(description_ru__isnull=True).update(
        description_ru=F("description")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0038_company_verification_document_and_more"),
    ]

    atomic = False

    operations = [
        migrations.AddField(
            model_name="businesscategory",
            name="name_uz",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="company",
            name="description_uz",
            field=models.TextField(blank=True, null=True),
        ),
        # `description_ru` already exists in the DB in some deployments;
        # avoid re-adding it to prevent DuplicateColumn errors. The
        # population step below will still run to ensure values are set.
        migrations.AddField(
            model_name="company",
            name="image_1200",
            field=models.ImageField(
                blank=True, null=True, upload_to="company_images/variants/"
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="image_400",
            field=models.ImageField(
                blank=True, null=True, upload_to="company_images/variants/"
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="image_800",
            field=models.ImageField(
                blank=True, null=True, upload_to="company_images/variants/"
            ),
        ),
        migrations.AddField(
            model_name="company",
            name="name_ru",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="company",
            name="name_uz",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(populate_translations, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="company",
            name="description_ru",
            field=models.TextField(blank=True, null=True),
        ),
    ]
