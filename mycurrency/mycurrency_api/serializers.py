from rest_framework import serializers
from .models import Provider, Currency, CurrencyExchangeRate
from django.conf import settings

# Accessing an available currencies from settings
PROVIDER_METHODS = settings.PROVIDER_METHODS


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["name", "api_url", "endpoints", "priority"]

    def validate_endpoints(self, value):
        """
        Check if the necessary endpoints exist in the 'endpoints' JSON field.
        """
        endpoints = value
        for i in PROVIDER_METHODS:
            if i not in endpoints.keys():
                raise serializers.ValidationError(
                    f"The '{i}' key is required in the 'endpoints'."
                )
        return value


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["code", "name", "symbol"]


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRate
        fields = [
            "source_currency",
            "exchanged_currency",
            "valuation_date",
            "rate_value",
        ]
