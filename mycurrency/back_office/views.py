from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.shortcuts import render
from mycurrency_api.operations import get_converted_data, get_currency_rates
from django.conf import settings
import json

# Accessing an available currencies from settings
AVAILABLE_CURRENCIES = settings.AVAILABLE_CURRENCIES


# Create your views here.
class Converter(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, format=None):
        """
        returns a template where online currency converting is possible.
        """
        return render(request, "converter.html")

    def post(self, request, format=None):
        """
        returns a template where online currency converting is possible, with results of the last request.
        """
        params_names = ["sourceCurrency", "amount", "targetCurrenciesList"]

        for param_name in params_names:
            if not param_name in request.data:
                context = {"error": f"Missing '{param_name}' parameter."}
                return render(request, "converter.html", context)

        source_currency = request.POST.get("sourceCurrency")
        amount = request.POST.get("amount")
        target_currencies = request.POST.getlist("targetCurrenciesList")

        context = {"result": {}}

        for target_currency in target_currencies:
            try:
                converted_data = get_converted_data(
                    [source_currency], [amount], [target_currency]
                )
                context["result"][target_currency] = converted_data
            except Exception as e:
                context["result"][target_currency] = {
                    "error": str(e),
                    "source_currency": source_currency,
                    "exchanged_currency": target_currency,
                }

        return render(request, "converter.html", context)


class Graph(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, format=None):
        """
        returns a template where it is possible to show currency rate value graph.
        """

        return render(request, "graph.html")

    def post(self, request, format=None):
        """
        Get exchange rates from dateFrom to dateTo and return it to show on the chart.
        """
        params_names = ["sourceCurrency", "dateFrom", "dateTo", "targetCurrenciesList"]

        for param_name in params_names:
            if not param_name in request.data:
                context = {"error": f"Missing '{param_name}' parameter."}
                return render(request, "converter.html", context)

        source_currency = request.POST.get("sourceCurrency")
        date_from = request.POST.get("dateFrom")
        date_to = request.POST.get("dateTo")
        target_currencies = request.POST.getlist("targetCurrenciesList")

        context = {"datasets": []}

        try:
            currency_rates = get_currency_rates(
                [source_currency], [date_from], [date_to]
            )
            context["labels"] = list(currency_rates["rates"].keys())
            for target_currency in target_currencies:
                label = f"{source_currency} - {target_currency}"
                data = []
                rates = currency_rates["rates"]
                for rate in rates:
                    if target_currency in rates[rate].keys():
                        data.append(rates[rate][target_currency])
                context["datasets"].append({"label": label, "data": data})

        except Exception as e:
            context = {"error": str(e)}

        return render(request, "graph.html", {"result": json.dumps(context)})
