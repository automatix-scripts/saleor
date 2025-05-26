# /home/ubuntu/platform-services/integration_settings_service/urls.py
# Autor: Szymon Fuchs
# Data: 27.09.2021

from django.urls import path
from .views import IntegrationSettingsView, IssueTrackingSettingsView

app_name = 'integration_settings_service'

urlpatterns = [
    path('api/v1/settings/marketplace/', IntegrationSettingsView.as_view(), name='marketplace_integration_settings_api'),
    path('api/v1/settings/issue-tracking/', IssueTrackingSettingsView.as_view(), name='issue_tracking_settings_api'),
]
