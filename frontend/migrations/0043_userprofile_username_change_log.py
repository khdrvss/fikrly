from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0042_alter_businesscategory_name_ru_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="username_change_log",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
