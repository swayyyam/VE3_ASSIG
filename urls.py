from django.urls import path
from .views import UploadCSVView, AnalyzeCSVView
from django.conf import settings
from django.conf.urls.static import static

app_name = "analysis"

urlpatterns = [
    path('', UploadCSVView.as_view(), name='upload_csv'),
    path('analyze/<int:pk>/', AnalyzeCSVView.as_view(), name='analyze_csv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL Configuration for the analysis app.

Includes two URL patterns:
1. upload_csv: URL for uploading CSV files.
2. analyze_csv: URL for analyzing uploaded CSV files.

Additionally serves media files in development.
"""
