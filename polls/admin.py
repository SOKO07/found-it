from django.contrib import admin
from .models import Question, Choice, Item
# Register your models here.
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Item)