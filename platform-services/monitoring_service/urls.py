# /home/ubuntu/platform-services/monitoring_service/urls.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from django.urls import path
from .views import HealthCheckView, ResourceMetricsDataView, RecentAlertsView

app_name = 'monitoring_service'

urlpatterns = [
    path('api/v1/monitoring/health/', HealthCheckView.as_view(), name='health_check_api'),
    path('api/v1/monitoring/resources/<int:resource_id>/metrics/', ResourceMetricsDataView.as_view(), name='resource_metrics_data_api'),
    path('api/v1/monitoring/alerts/', RecentAlertsView.as_view(), name='recent_alerts_api'),
]
