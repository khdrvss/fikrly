# Generated migration to remove phone verification functionality
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("frontend", "0039_businesscategory_name_uz_company_description_uz_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="PhoneOTP",
        ),
    ]
