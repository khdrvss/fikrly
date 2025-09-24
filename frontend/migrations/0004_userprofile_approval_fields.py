from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0003_add_userprofile_and_review_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='requested_approval_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
