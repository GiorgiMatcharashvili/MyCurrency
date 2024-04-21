from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class ProvidersAPITest(TestCase):
    fixtures = ["default_providers.json"]

    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/v1/providers/"
        self.add_data = {
            "name": "test",
            "api_url": "http://127.0.0.1:8000/",
            "endpoints": {
                "symbols": [
                    "timeseries",
                    "access_key",
                    "start_date",
                    "end_date",
                    "symbols",
                ],
                "converter": [
                    "convert",
                    "access_key",
                    "date_from",
                    "to",
                    "amount",
                    "symbols",
                ],
                "historical": ["date", "access_key", "base", "symbols"],
                "test": ["date", "access_key", "test", "test"],
            },
            "priority": 3,
        }
        self.prioritize_data = {"name": "Mock", "priority": 1}
        self.delete_data = {"name": "Fixer"}
        self.client = APIClient()

    def test_list_providers(self):
        response = self.client.get(self.url)

        self.assertEqual(2, len(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_provider(self):
        response = self.client.post(self.url, self.add_data, format="json")

        self.assertIn("name", response.data)
        self.assertIn("api_url", response.data)
        self.assertIn("endpoints", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_prioritize_provider(self):
        response = self.client.put(self.url, self.prioritize_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_provider(self):
        response = self.client.delete(self.url, self.delete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RatesAPITest(TestCase):
    fixtures = ["test_provider.json"]

    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/v1/rates/?source_currency=EUR&date_from=2024-01-01&date_to=2024-01-04"
        self.client = APIClient()

    def test_get_rates(self):
        response = self.client.get(self.url)

        self.assertIn("source_currency", response.data)
        self.assertIn("date_from", response.data)
        self.assertIn("date_to", response.data)
        self.assertIn("rates", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ConverterAPITest(TestCase):
    fixtures = ["test_provider.json"]

    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/v1/convert/?source_currency=EUR&amount=10.0&exchanged_currency=USD"
        self.client = APIClient()

    def test_convert_currency(self):
        response = self.client.get(self.url)

        self.assertIn("source_currency", response.data)
        self.assertIn("exchanged_currency", response.data)
        self.assertIn("initial_amount", response.data)
        self.assertIn("rate", response.data)
        self.assertIn("result", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TWRRAPITest(TestCase):
    fixtures = ["test_provider.json"]

    def setUp(self):
        self.url = "http://127.0.0.1:8000/api/v1/twrr/?source_currency=EUR&amount=20&exchanged_currency=USD&start_date=2024-04-17"
        self.client = APIClient()

    def test_get_twrr_values(self):
        response = self.client.get(self.url)

        self.assertIn("source_currency", response.data)
        self.assertIn("exchanged_currency", response.data)
        self.assertIn("initial_amount", response.data)
        self.assertIn("start_date", response.data)
        self.assertIn("result", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
