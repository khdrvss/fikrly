from django.db import migrations, models
from django.db.models import F


def copy_logo_url_to_backup(apps, schema_editor):
    Company = apps.get_model("frontend", "Company")
    Company.objects.exclude(logo_url="").update(logo_url_backup=F("logo_url"))


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0040_remove_phoneotp"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="logo_url_backup",
            field=models.URLField(
                blank=True,
                editable=False,
                help_text="Logo URL zaxirasi (avtomatik saqlanadi)",
            ),
        ),
        migrations.RunPython(copy_logo_url_to_backup, migrations.RunPython.noop),
    ]
