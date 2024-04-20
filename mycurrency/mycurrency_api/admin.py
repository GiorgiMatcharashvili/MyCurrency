from django.contrib import admin
from .models import Provider, CurrencyExchangeRate, Currency

# Register your models here.
admin.site.register(Provider)
admin.site.register(CurrencyExchangeRate)
admin.site.register(Currency)
