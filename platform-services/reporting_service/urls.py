# /home/ubuntu/platform-services/reporting_service/urls.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

from django.urls import path
from .views import (
    SalesReportView,
    ProductPerformanceReportView,
    AsyncReportRequestView,
    AsyncReportStatusView
)

app_name = 'reporting_service'

urlpatterns = [
    path('api/v1/reports/sales-summary/', SalesReportView.as_view(), name='sales_summary_report'),
    path('api/v1/reports/product-performance/', ProductPerformanceReportView.as_view(), name='product_performance_report'),
    path('api/v1/reports/async/request/', AsyncReportRequestView.as_view(), name='async_report_request'),
    path('api/v1/reports/async/status/<str:task_id>/', AsyncReportStatusView.as_view(), name='async_report_status'),
]
