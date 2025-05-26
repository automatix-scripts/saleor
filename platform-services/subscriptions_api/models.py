# /home/ubuntu/platform-services/subscriptions_api/models.py
# Autor: Szymon Fuchs
# Data: 25.08.2021

from django.db import models

class UserSubscription(models.Model):
    user_email = models.EmailField(unique=True) 
    plan_name = models.CharField(max_length=100)
    saleor_product_variant_id = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    domain_name = models.CharField(max_length=255, blank=True, null=True)
    allegro_account_info = models.TextField(blank=True, null=True)
    saleor_order_id = models.CharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return f"{self.user_email} - {self.plan_name} ({'Active' if self.is_active else 'Inactive'})"
