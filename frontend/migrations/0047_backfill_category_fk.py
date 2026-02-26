"""
Data migration: backfill Company.category_fk from Company.category (CharField).

For every company whose category_fk is NULL, attempt to find a BusinessCategory
whose name matches the string value stored in the category field (case-insensitive).
If a match is found the FK is set; unmatched rows are left unchanged.

Running this migration twice is safe because it only touches rows where
category_fk IS NULL.
"""
from django.db import migrations


def backfill_category_fk(apps, schema_editor):
    Company = apps.get_model("frontend", "Company")
    BusinessCategory = apps.get_model("frontend", "BusinessCategory")

    # Build a name→id lookup (case-insensitive)
    category_map = {cat.name.strip().lower(): cat.id for cat in BusinessCategory.objects.all()}

    companies_to_update = Company.objects.filter(category_fk__isnull=True).exclude(category="")
    updated = 0
    for company in companies_to_update.iterator(chunk_size=500):
        cat_id = category_map.get(company.category.strip().lower())
        if cat_id:
            company.category_fk_id = cat_id
            company.save(update_fields=["category_fk"])
            updated += 1

    print(f"\n  Backfilled category_fk for {updated} companies.")


def reverse_backfill(apps, schema_editor):
    # Irreversible in practice (we don't clear category_fk on reverse because
    # the FK may have been set correctly before this migration ran).
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0046_remove_twofactorauth"),
    ]

    operations = [
        migrations.RunPython(backfill_category_fk, reverse_backfill),
    ]
