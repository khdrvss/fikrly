from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-review_count', '-rating', 'name']

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    company = models.ForeignKey(Company, related_name='reviews', on_delete=models.CASCADE)
    user_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user_name} → {self.company.name} ({self.rating})"
