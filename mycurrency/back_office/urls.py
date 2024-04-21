from django.urls import path
from .views import Converter, Graph

urlpatterns = [
    path("converter/", Converter.as_view(), name="back_office_converter"),
    path("graph/", Graph.as_view(), name="back_office_graph"),
]
