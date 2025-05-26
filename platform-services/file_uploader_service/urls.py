# /home/ubuntu/platform-services/file_uploader_service/urls.py
# Autor: Szymon Fuchs
# Data: 20.08.2021

from django.urls import path
from .views import CompanyGalleryUploadView

urlpatterns = [
    path('upload-company-image/', CompanyGalleryUploadView.as_view(), name='upload_company_image'),
]
