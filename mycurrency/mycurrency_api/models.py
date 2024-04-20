from django.db import models
from django.conf import settings

FIXER_API_URL = settings.FIXER_API_URL


class Provider(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)
    api_url = models.URLField()
    endpoints = models.JSONField()
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, db_index=True)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(
        Currency, related_name="exchanges", on_delete=models.CASCADE
    )
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18)

    def __str__(self):
        return f"{self.source_currency.code} to {self.exchanged_currency.code} at {self.valuation_date}"
