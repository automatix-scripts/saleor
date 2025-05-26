# /home/ubuntu/platform-services/template_management_service/urls.py
# Autor: Szymon Fuchs
# Data: 20.09.2021

from django.urls import path
from .views import TemplateListView, TemplateDetailView

urlpatterns = [
    path('list/', TemplateListView.as_view(), name='template_list_api'),
    path('detail/<str:template_id>/', TemplateDetailView.as_view(), name='template_detail_api'),
]
