# /home/ubuntu/platform-services/gus_integration_service/urls.py
# Autor: Szymon Fuchs
# Data: 03.09.2021

from django.urls import path
from .views import GetCompanyDataByNipView

urlpatterns = [
    path('get-company-by-nip/', GetCompanyDataByNipView.as_view(), name='get_company_by_nip'),
]
