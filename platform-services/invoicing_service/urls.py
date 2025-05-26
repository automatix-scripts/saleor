# /home/ubuntu/platform-services/invoicing_service/urls.py
# Autor: Szymon Fuchs
# Data: 30.08.2021

from django.urls import path
from .webhook_handlers import saleor_order_to_invoice_webhook

urlpatterns = [
    path('webhooks/saleor/order-to-invoice/', saleor_order_to_invoice_webhook, name='webhook_order_to_invoice'),
]
