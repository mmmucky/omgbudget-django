from django.contrib import admin

# Register your models here.
from .models import Transaction, Classification

admin.site.register(Transaction)
admin.site.register(Classification)
