from django.db import migrations


class Migration(migrations.Migration):
    """
    Drop the legacy `Category` model.  `BusinessCategory` (added in 0025) is
    the canonical category model used by all live views, forms and queries.
    The `Category` table had no foreign-key dependants and was only reachable
    from admin.py and the now-deleted `populate_categories` management command.
    """

    dependencies = [
        ("frontend", "0047_backfill_category_fk"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Category",
        ),
    ]
