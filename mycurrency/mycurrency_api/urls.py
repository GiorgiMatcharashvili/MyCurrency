from django.urls import re_path
from .views import Providers, Rates, Converter, TWRR

urlpatterns = [
    re_path(
        r"^(?P<version>(v1|v2))/providers/$", Providers.as_view(), name="providers"
    ),
    re_path(r"^(?P<version>(v1|v2))/rates/$", Rates.as_view(), name="rates"),
    re_path(r"^(?P<version>(v1|v2))/convert/$", Converter.as_view(), name="converter"),
    re_path(r"^(?P<version>(v1|v2))/twrr/$", TWRR.as_view(), name="twrr"),
]
