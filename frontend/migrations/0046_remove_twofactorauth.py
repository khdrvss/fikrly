from django.db import migrations


class Migration(migrations.Migration):
    """Drop the unused TwoFactorAuth table."""

    dependencies = [
        ("frontend", "0045_fix_duplicate_reviews_constraint"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TwoFactorAuth",
        ),
    ]
