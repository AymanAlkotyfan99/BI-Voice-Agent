from django.urls import path
from .views import RunExtractorView

urlpatterns = [
    path("run/", RunExtractorView.as_view()),
]
