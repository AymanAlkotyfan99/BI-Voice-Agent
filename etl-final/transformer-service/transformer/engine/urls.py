from django.urls import path
from .views import TestTransformView

urlpatterns = [
    path("test/", TestTransformView.as_view()),
]
