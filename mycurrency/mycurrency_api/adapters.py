from abc import ABC, abstractmethod
import random
from .models import Provider
from .drivers import BaseDriver, MockDriver
from django.conf import settings

# Accessing an available currencies from settings
FIXER_ACCESS_KEY = settings.FIXER_ACCESS_KEY
AVAILABLE_CURRENCIES = settings.AVAILABLE_CURRENCIES


# Abstract class for provider
class AbstractAdapter(ABC):
    @abstractmethod
    def get_exchange_rate_data(
        self, source_currency: str, exchanged_currency: str, valuation_date: str
    ):
        pass

    @abstractmethod
    def get_currency_symbols(self):
        pass

    @abstractmethod
    def convert_currencies(
        self, source_currency: str, exchanged_currency: str, amount: float
    ):
        pass


# Provider Adapter class
class Adapter(AbstractAdapter):
    def __init__(self):
        # Get active providers
        self.active_providers = Provider.objects.filter(priority__gt=0).order_by(
            "priority"
        )

    def get_exchange_rate_data(
        self,
        source_currency: str,
        exchanged_currency: str,
        valuation_date: str,
        *args,
        **kwargs
    ):
        """
        Run historical method for every provider sorted by priority, return data if exists.
        """
        self.update_adapters()

        for provider in self.active_providers:
            if provider.name == "Mock":
                driver = MockDriver()
                rates = driver.historical(date=valuation_date, base=source_currency)

            elif provider.name == "Fixer":
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                rates = driver.historical(
                    endpoint=valuation_date,
                    access_key=FIXER_ACCESS_KEY,
                    base=source_currency,
                )

            else:
                # default Provider
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                rates = driver.historical(*args, **kwargs)

            if not rates:
                continue
            return rates

        raise Exception("Providers were unable to gather rate data.")

    def get_currency_symbols(self, *args, **kwargs):
        """
        Run symbols method for every provider sorted by priority, return data if exists.
        """
        self.update_adapters()

        for provider in self.active_providers:
            if provider.name == "Mock":
                driver = MockDriver()
                symbols = driver.symbols()

            elif provider.name == "Fixer":
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                symbols = driver.symbols(access_key=FIXER_ACCESS_KEY)

            else:
                # default Provider
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                symbols = driver.symbols(*args, **kwargs)

            if not symbols:
                continue
            return symbols

        raise Exception("Providers were unable to gather symbols.")

    def convert_currencies(
        self,
        source_currency: str,
        exchanged_currency: str,
        amount: float,
        *args,
        **kwargs
    ):
        """
        Run converter method for every provider sorted by priority, return data if exists.
        """
        self.update_adapters()

        for provider in self.active_providers:
            if provider.name == "Mock":
                driver = MockDriver()
                converted_data = driver.converter(
                    source_currency, exchanged_currency, amount
                )

            elif provider.name == "Fixer":
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                converted_data = driver.converter(
                    access_key=FIXER_ACCESS_KEY,
                    currency_from=source_currency,
                    to=exchanged_currency,
                    amount=amount,
                )

            else:
                # default Provider
                driver = BaseDriver(api_url=provider.api_url, **provider.endpoints)
                converted_data = driver.converter(*args, **kwargs)

            if not converted_data:
                continue
            return converted_data

        raise Exception("Providers were unable to convert currencies.")

    def update_adapters(self):
        """
        Update active providers list and order them by priority.
        """
        self.active_providers = Provider.objects.filter(priority__gt=0).order_by(
            "priority"
        )
