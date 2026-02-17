from django.db import migrations
from django.utils.text import slugify


def rename_category(apps, schema_editor):
    BusinessCategory = apps.get_model("frontend", "BusinessCategory")
    Company = apps.get_model("frontend", "Company")

    # Update BusinessCategory
    try:
        cat = BusinessCategory.objects.get(name="Avtomobilsozlik")
        cat.name = "Avto kompaniyalar"
        cat.slug = slugify("Avto kompaniyalar")
        cat.save()
    except BusinessCategory.DoesNotExist:
        pass

    # Update Company strings (if any still rely on the string field)
    Company.objects.filter(category="Avtomobilsozlik").update(
        category="Avto kompaniyalar"
    )


def reverse_rename(apps, schema_editor):
    BusinessCategory = apps.get_model("frontend", "BusinessCategory")
    Company = apps.get_model("frontend", "Company")

    try:
        cat = BusinessCategory.objects.get(name="Avto kompaniyalar")
        cat.name = "Avtomobilsozlik"
        cat.slug = slugify("Avtomobilsozlik")
        cat.save()
    except BusinessCategory.DoesNotExist:
        pass

    Company.objects.filter(category="Avto kompaniyalar").update(
        category="Avtomobilsozlik"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0033_alter_activitylog_action_and_more"),
    ]

    operations = [
        migrations.RunPython(rename_category, reverse_rename),
    ]
