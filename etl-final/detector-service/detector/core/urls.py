from django.urls import path
from .views import RunDetectorView

urlpatterns = [
    path("run-detector/", RunDetectorView.as_view(), name="run-detector"),
]
