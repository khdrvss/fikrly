from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0043_userprofile_username_change_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="businesscategory",
            name="is_active",
            field=models.BooleanField(
                default=True,
                verbose_name="Faol",
                help_text=(
                    "Agar o'chirilsa, bu kategoriya va uning barcha kompaniyalari"
                    " saytda ko'rinmaydi"
                ),
            ),
        ),
    ]
