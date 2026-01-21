# Generated migration for performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0035_reviewhelpfulvote_review_helpful_count_and_more'),
    ]

    operations = [
        # Add index for sorting by like_count (most liked)
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['company', 'is_approved', '-like_count'], name='frontend_re_company_liked_idx'),
        ),
        # Add index for company view count sorting
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['-view_count'], name='frontend_co_view_co_idx'),
        ),
        # Add index for category filtering
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['category_fk', 'is_active', '-rating'], name='frontend_co_cat_act_rat_idx'),
        ),
        # Add index for user's review listing
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['user', '-created_at'], name='frontend_re_user_created_idx'),
        ),
    ]
