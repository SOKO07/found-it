import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

class PendingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    STATUS_CHOICES = [
        ('not_at_repository', 'Not at Repository'),
        ('at_repository', 'At Repository'),
        ('retrieved', 'Retrieved'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    pending_category_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True)
    found_location = models.CharField(max_length=100)
    found_date = models.DateField(verbose_name='date found')
    pub_date = models.DateTimeField(verbose_name='date published')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_at_repository')
    retrieved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrieved_items')
    held_by = models.ManyToManyField(User, blank=True, related_name='held_items')

    def __str__(self):
        return self.name
    
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now