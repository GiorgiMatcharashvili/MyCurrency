import requests
import random
import time
from django.conf import settings
from datetime import datetime, timedelta

# Accessing an available currencies from settings
AVAILABLE_CURRENCIES = settings.AVAILABLE_CURRENCIES


class BaseDriver:
    def __init__(self, api_url: str, *args, **kwargs):
        """
        Initialize the Base Driver and create endpoint methods.
        """
        self.API_URL = api_url
        for method_name, endpoint_args in kwargs.items():
            setattr(
                self,
                method_name,
                self._create_endpoint_method(method_name, endpoint_args),
            )

    def _create_endpoint_method(self, method_name, endpoint_args):
        """
        Endpoint methods are functions which connects method to an endpoint,
        each method is connected to a specific endpoint which is called when method is called.
        """

        def method(*args, **kwargs):
            if len(kwargs) == len(endpoint_args):
                # You can also pass endpoint name as argument, in case endpoint name is parameter
                endpoint_name = endpoint_args.pop(0)
                if "endpoint" in kwargs.keys():
                    endpoint_name = kwargs.pop("endpoint")
            else:
                # Get pre-written endpoint name
                endpoint_name = endpoint_args.pop(0)

            # Handle argument errors
            kwargs_diff = set(kwargs.keys()) - set(endpoint_args)
            endpoint_args_diff = set(endpoint_args) - set(kwargs.keys())

            if endpoint_args_diff:
                raise TypeError(
                    f"{method_name} missing required positional arguments: {endpoint_args_diff}"
                )

            if kwargs_diff:
                raise TypeError(
                    f"{method_name} takes {endpoint_args} positional arguments but {kwargs_diff} were given"
                )

            # Make request
            url = self.API_URL + endpoint_name

            if method_name == "converter":
                # Fixer.io convert method requires argument to be named 'from',
                # But it is not possible in python
                if "currency_from" in kwargs.keys():
                    kwargs["from"] = kwargs["currency_from"]
                    kwargs.pop("currency_from")

            result = requests.get(url, params=kwargs).json()

            if not result["success"]:
                # If it's not a success return False
                return False

            return result

        return method


class MockDriver:
    """
    Mock driver mocks necessary endpoints for testing purposes.
    """

    @staticmethod
    def generate_random_rate():
        start_number = random.randint(1, 5)
        return random.uniform(start_number, start_number + 1)

    def converter(self, currency_from, to, amount):
        timestamp = str(int(time.time()))
        date = str(datetime.now().date())

        rate = self.generate_random_rate()
        result = amount * rate

        return {
            "success": "true",
            "query": {"from": currency_from, "to": to, "amount": amount},
            "info": {"timestamp": timestamp, "rate": self.generate_random_rate()},
            "historical": "",
            "date": date,
            "result": result,
        }

    def historical(self, date, base):
        timestamp = str(int(time.time()))

        rates = {}

        for i in AVAILABLE_CURRENCIES:
            rates[i] = self.generate_random_rate()

        return {
            "success": True,
            "historical": True,
            "date": date,
            "timestamp": timestamp,
            "base": base,
            "rates": rates,
        }

    def symbols(self):
        return {
            "success": True,
            "symbols": {
                "EUR": "Euro",
                "CHF": "Swiss Franc",
                "USD": "United States Dollar",
                "GBP": "British Pound Sterling",
            },
        }
