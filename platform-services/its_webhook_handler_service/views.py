# /home/ubuntu/platform-services/its_webhook_handler_service/views.py
# Autor: Szymon Fuchs
# Data: 30.09.2021

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import requests

# ITS_API_URL = getattr(settings, 'ITS_API_URL', 'https://api.example-its.com/v1/tickets')
# ITS_API_KEY = getattr(settings, 'ITS_API_KEY', 'your_its_api_key')
# SALEOR_WEBHOOK_SECRET = getattr(settings, 'SALEOR_WEBHOOK_SECRET_FOR_ITS', None)

# def verify_saleor_signature(body, signature, secret):
#    # Implementacja weryfikacji sygnatury webhooka Saleor
#    # import hashlib
#    # import hmac
#    # if not secret or not signature: return False
#    # expected_signature = hmac.new(key=secret.encode('utf-8'), msg=body, digestmod=hashlib.sha256).hexdigest()
#    # return hmac.compare_digest(expected_signature, signature)
#    return True # Uproszczenie - w produkcji weryfikacja jest kluczowa

@csrf_exempt
@require_POST
def saleor_event_to_its_webhook(request):
    # if not verify_saleor_signature(request.body, request.headers.get('X-Saleor-Signature'), SALEOR_WEBHOOK_SECRET):
    #     return HttpResponse('Invalid signature', status=403)

    try:
        payload = json.loads(request.body)
        event_type = request.headers.get('X-Saleor-Event')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    print(f"Received Saleor webhook event for ITS: {event_type}")

    if event_type == 'ORDER_CREATED' or event_type == 'order_created': # Nazwy mogą się różnić
        order_id = payload.get('id') or payload.get('order', {}).get('id')
        user_email = payload.get('user_email') or payload.get('order', {}).get('user_email')
        order_number = payload.get('number') or payload.get('order', {}).get('number')
        
        ticket_title = f"Nowe zamówienie Saleor: #{order_number}"
        ticket_description = f"Zamówienie od: {user_email}. ID Saleor: {order_id}."
        
        # its_api_url = getattr(settings, 'ITS_API_URL_PLACEHOLDER', None)
        # its_api_key = getattr(settings, 'ITS_API_KEY_PLACEHOLDER', None)
        # if its_api_url and its_api_key:
        #     its_payload = {'title': ticket_title, 'description': ticket_description, 'requester_email': user_email}
        #     headers = {'Authorization': f'Bearer {its_api_key}', 'Content-Type': 'application/json'}
        #     try:
        #         response = requests.post(its_api_url, json=its_payload, headers=headers, timeout=10)
        #         response.raise_for_status()
        #         print(f"Ticket created in ITS: {response.json().get('id')}")
        #     except requests.exceptions.RequestException as e:
        #         print(f"Error creating ticket in ITS for order {order_number}: {e}")
        #         return JsonResponse({'error': 'Failed to create ticket in ITS'}, status=502)
        # else:
        #      print("ITS API URL or Key not configured. Skipping ticket creation.")
        print(f"Symulacja utworzenia ticketa w ITS dla zamówienia: {order_number}. Email: {user_email}")
    
    return HttpResponse(status=200)
