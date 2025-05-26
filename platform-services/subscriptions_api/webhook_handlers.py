# /home/ubuntu/platform-services/subscriptions_api/webhook_handlers.py
# Autor: Szymon Fuchs
# Data: 25.08.2021

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import json
from .models import UserSubscription

@csrf_exempt
@require_POST
def saleor_order_paid_webhook(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    order_id = payload.get('order', {}).get('id')
    user_email = payload.get('order', {}).get('user_email')
    lines = payload.get('order', {}).get('lines', [])
    
    order_metadata = payload.get('order', {}).get('metadata', {}) 
    domain_name_from_meta = next((item['value'] for item in order_metadata if item['key'] == 'chosen_domain'), None)
    allegro_info_from_meta = next((item['value'] for item in order_metadata if item['key'] == 'allegro_details'), None)

    if not all([order_id, user_email, lines]):
        return JsonResponse({'error': 'Missing order data in webhook'}, status=400)

    for line in lines:
        variant_id = line.get('variant', {}).get('id')
        product_name = line.get('product_name')
        
        duration_days = 30 
        if "roczny" in product_name.lower() or "annual" in product_name.lower():
            duration_days = 365
        elif "miesięczny" in product_name.lower() or "monthly" in product_name.lower():
            duration_days = 30
        
        end_date = timezone.now() + timedelta(days=duration_days)

        subscription, created = UserSubscription.objects.update_or_create(
            user_email=user_email,
            defaults={
                'plan_name': product_name,
                'saleor_product_variant_id': variant_id,
                'start_date': timezone.now(),
                'end_date': end_date,
                'is_active': True,
                'domain_name': domain_name_from_meta,
                'allegro_account_info': allegro_info_from_meta,
                'saleor_order_id': order_id
            }
        )
        if created:
            print(f"Created new subscription for {user_email}, plan {product_name}")
        else:
            print(f"Updated subscription for {user_email}, plan {product_name}")

    return HttpResponse(status=200)
