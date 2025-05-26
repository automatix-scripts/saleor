# /home/ubuntu/platform-services/gov_data_integration_service/urls.py
# Autor: Szymon Fuchs
# Data: 15.09.2021

from django.urls import path
from .views import CeidgDataView, KrsDataView

urlpatterns = [
    path('ceidg-data/', CeidgDataView.as_view(), name='ceidg_data'),
    path('krs-data/', KrsDataView.as_view(), name='krs_data'),
]
