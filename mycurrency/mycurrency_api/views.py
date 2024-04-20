from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProviderSerializer
from .models import Provider
from rest_framework import status
from .operations import get_currency_rates, get_converted_data, get_twrr_values


class Providers(APIView):
    def get(self, request, format=None):
        """
        List all providers
        """
        providers = [
            {"name": i.name, "api_url": i.api_url, "priority": i.priority}
            for i in Provider.objects.all()
        ]
        return Response(providers, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """
        Create new provider
        """
        serializer = ProviderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        """
        Delete the provider
        """
        provider_name = request.data.get("name")
        if not provider_name:
            return Response(
                {"error": "Missing 'name' parameter in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Attempt to retrieve the provider instance
            provider = Provider.objects.get(name=provider_name)
        except Provider.DoesNotExist:
            return Response(
                {"error": "Provider not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete the provider instance
        provider.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, format=None):
        """
        Prioritize the provider
        """
        provider_name = request.data.get("name")
        priority = request.data.get("priority")

        if not provider_name:
            return Response(
                {"error": "Missing 'name' parameter in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not str(priority):
            return Response(
                {"error": "Missing 'priority' parameter in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Attempt to retrieve the provider instance
            provider = Provider.objects.get(name=provider_name)
        except Provider.DoesNotExist:
            return Response(
                {"error": "Provider not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if (
            Provider.objects.filter(priority=priority)
            .exclude(name=provider.name)
            .exists()
        ):

            for i in Provider.objects.filter(priority__gte=priority).exclude(
                name=provider.name
            ):
                i.priority += 1
                i.save()

        provider.priority = priority
        provider.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Rates(APIView):
    def get(self, request, format=None):
        """
        returns a time series list of rate values for each available Currency.
        """
        params_names = ["source_currency", "date_from", "date_to"]

        for param_name in params_names:
            if not param_name in request.query_params:
                return Response(
                    {"error": f"Missing '{param_name}' parameter in query"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            currency_rates = get_currency_rates(**request.query_params)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(currency_rates, status=status.HTTP_200_OK)


class Converter(APIView):
    def get(self, request, format=None):
        """
        returns an object containing the rate value between source and exchanges currencies.
        """
        data_names = ["source_currency", "amount", "exchanged_currency"]

        for data_name in data_names:
            if not data_name in request.query_params:
                return Response(
                    {"error": f"Missing '{data_name}' parameter in query"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            converted = get_converted_data(**request.query_params)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(converted, status=status.HTTP_200_OK)


class TWRR(APIView):
    def get(self, request, format=None):
        """
        returns  a historical time series list of TWRR values for each
        available historical exchange rates for both (source/exchanged) Currencies.
        """

        data_names = ["source_currency", "amount", "exchanged_currency", "start_date"]

        for data_name in data_names:
            if not data_name in request.query_params:
                return Response(
                    {"error": f"Missing '{data_name}' parameter in query"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            twrr_values = get_twrr_values(**request.query_params)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(twrr_values, status=status.HTTP_200_OK)
