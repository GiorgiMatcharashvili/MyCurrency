from django.core.management.base import BaseCommand
import json
from django.conf import settings
from django.core.cache import cache
import os

# Accessing an available currencies from settings
BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("json_file", nargs="+", type=str)

    def handle(self, *args, **options):
        json_file = options["json_file"][0]

        # Open and parse the JSON file
        with open(
            os.path.join(BASE_DIR, "mycurrency_api/fixtures/", json_file), "r"
        ) as f:
            data = json.load(f)

        for redis_id, rate_value in data.items():
            cache.set(redis_id, rate_value, timeout=60 * 60)
