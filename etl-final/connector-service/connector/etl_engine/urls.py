from django.urls import path
from .views import UploadFileView, ConnectDBView

urlpatterns = [
    path("upload/", UploadFileView.as_view()),
    path("connect-db/", ConnectDBView.as_view()),
]
