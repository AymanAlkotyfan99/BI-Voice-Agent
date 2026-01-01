"""
URL Configuration for BI Voice Agent
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.auth_urls')),
    path('user/', include('users.user_urls')),
    path('workspace/', include('workspace.urls')),
    path('database/', include('database.urls')),
]

