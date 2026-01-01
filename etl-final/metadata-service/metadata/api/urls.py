from django.urls import path
from .views import (
    ConnectionLogsView,
    SchemaLogsView,
    ExtractLogsView,
    TransformLogsView,
    LoadLogsView,
)

urlpatterns = [
    path("logs/connections/", ConnectionLogsView.as_view()),
    path("logs/schema/", SchemaLogsView.as_view()),
    path("logs/extract/", ExtractLogsView.as_view()),
    path("logs/transform/", TransformLogsView.as_view()),
    path("logs/load/", LoadLogsView.as_view()),
]
