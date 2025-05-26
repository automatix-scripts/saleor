# /home/ubuntu/platform-services/its_webhook_handler_service/urls.py
# Autor: Szymon Fuchs
# Data: 30.09.2021

from django.urls import path
from .views import saleor_event_to_its_webhook

urlpatterns = [
    path('webhooks/saleor/its-trigger/', saleor_event_to_its_webhook, name='webhook_saleor_its_trigger'),
]
