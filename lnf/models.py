import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class PendingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "pending categories"

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = [
        ('not_at_repository', 'Not at Prefect Office'),
        ('at_repository', 'At Prefect Office'),
        ('retrieved', 'Retrieved'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, db_index=True)
    pending_category_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='item_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])]
    )
    found_location = models.CharField(max_length=100)
    found_date = models.DateField(verbose_name='date found', db_index=True)
    pub_date = models.DateTimeField(verbose_name='date published')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_at_repository', db_index=True)
    retrieved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrieved_items')
    held_by = models.ManyToManyField(User, blank=True, related_name='held_items')

    def __str__(self):
        return self.name
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now