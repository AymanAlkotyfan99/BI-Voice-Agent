"""
URL Configuration for BI Voice Agent
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.auth_urls')),
    path('user/', include('users.user_urls')),
    path('workspace/', include('workspace.urls')),
    path('database/', include('database.urls')),
    path('voice-reports/', include('voice_reports.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

