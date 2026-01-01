from django.urls import path
from .views import TestLoaderView

urlpatterns = [
    path("test/", TestLoaderView.as_view()),
]
