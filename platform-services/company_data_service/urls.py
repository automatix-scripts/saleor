# /home/ubuntu/platform-services/company_data_service/urls.py
# Autor: Szymon Fuchs
# Data: 23.08.2021

from django.urls import path
from .views import ValidateCompanyIdentifiersView

urlpatterns = [
    path('validate-identifiers/', ValidateCompanyIdentifiersView.as_view(), name='validate_identifiers'),
]
