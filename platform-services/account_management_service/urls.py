# /home/ubuntu/platform-services/account_management_service/urls.py
# Autor: Szymon Fuchs
# Data: 18.08.2021

from django.urls import path
from .views import RequestEmailChangeView, ConfirmEmailChangeView

urlpatterns = [
    path('request-email-change/', RequestEmailChangeView.as_view(), name='request_email_change'),
    path('confirm-email-change/<str:token>/', ConfirmEmailChangeView.as_view(), name='confirm_email_change'),
]
