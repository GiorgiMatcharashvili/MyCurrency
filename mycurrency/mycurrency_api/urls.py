from django.urls import path
from .views import Providers, Rates, Converter, TWRR

urlpatterns = [
    path("providers/", Providers.as_view(), name="providers"),
    path("rates/", Rates.as_view(), name="currencies"),
    path("convert/", Converter.as_view(), name="converter"),
    path("twrr/", TWRR.as_view(), name="twrr"),
]
