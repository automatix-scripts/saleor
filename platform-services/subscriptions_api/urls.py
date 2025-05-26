# /home/ubuntu/platform-services/subscriptions_api/urls.py
# Autor: Szymon Fuchs
# Data: 25.08.2021

from django.urls import path
from .webhook_handlers import saleor_order_paid_webhook

urlpatterns = [
    path('webhooks/saleor/order-paid/', saleor_order_paid_webhook, name='webhook_saleor_order_paid'),
]
