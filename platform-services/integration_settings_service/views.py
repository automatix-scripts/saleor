# /home/ubuntu/platform-services/integration_settings_service/views.py
# Autor: Szymon Fuchs
# Data: 27.09.2021

from django.http import JsonResponse
from django.views import View
from .models import MarketplaceIntegrationSettings, IssueTrackingSystemSettings
from .encryption_utils import encrypt_value # decrypt_value can be used when retrieving if needed
import json

class IntegrationSettingsView(View):
    async def get(self, request, *args, **kwargs):
        owner_id = request.GET.get('owner_identifier')
        marketplace_name = request.GET.get('marketplace_name')

        if not owner_id:
            return JsonResponse({'error': 'Owner identifier (owner_identifier) missing in query parameters'}, status=400)
        if not marketplace_name:
            return JsonResponse({'error': 'Marketplace name (marketplace_name) missing in query parameters'}, status=400)
            
        try:
            setting = MarketplaceIntegrationSettings.objects.get(owner_identifier=owner_id, marketplace_name=marketplace_name)
            data_to_return = {
                'owner_identifier': setting.owner_identifier,
                'marketplace_name': setting.marketplace_name,
                'is_active': setting.is_active,
                'sync_products_enabled': setting.sync_products_enabled,
                'sync_orders_enabled': setting.sync_orders_enabled,
                'last_successful_sync': setting.last_successful_sync.isoformat() if setting.last_successful_sync else None,
                'additional_config': setting.additional_config,
                'updated_at': setting.updated_at.isoformat()
            }
            return JsonResponse(data_to_return)
        except MarketplaceIntegrationSettings.DoesNotExist:
            return JsonResponse({'error': 'Marketplace settings not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

        owner_id = data.get('owner_identifier')
        marketplace_name = data.get('marketplace_name')

        if not owner_id:
            return JsonResponse({'error': 'Missing required field: owner_identifier'}, status=400)
        if not marketplace_name:
            return JsonResponse({'error': 'Missing required field: marketplace_name'}, status=400)

        api_key = data.get('api_key_placeholder')
        api_secret = data.get('api_secret_placeholder')
        is_active = data.get('is_active', False)
        sync_products = data.get('sync_products_enabled', False)
        sync_orders = data.get('sync_orders_enabled', False)
        additional_config = data.get('additional_config', {})

        if not isinstance(is_active, bool):
            return JsonResponse({'error': 'Invalid type for is_active, boolean expected'}, status=400)
        if not isinstance(sync_products, bool):
            return JsonResponse({'error': 'Invalid type for sync_products_enabled, boolean expected'}, status=400)
        if not isinstance(sync_orders, bool):
            return JsonResponse({'error': 'Invalid type for sync_orders_enabled, boolean expected'}, status=400)
        if not isinstance(additional_config, dict):
            return JsonResponse({'error': 'Invalid type for additional_config, JSON object expected'}, status=400)

        encrypted_api_key_placeholder = encrypt_value(api_key) if api_key is not None else None
        encrypted_api_secret_placeholder = encrypt_value(api_secret) if api_secret is not None else None
        
        defaults_to_update = {
            'is_active': is_active,
            'sync_products_enabled': sync_products,
            'sync_orders_enabled': sync_orders,
            'additional_config': additional_config,
        }
        if encrypted_api_key_placeholder is not None:
            defaults_to_update['api_key_placeholder'] = encrypted_api_key_placeholder
        if encrypted_api_secret_placeholder is not None:
             defaults_to_update['api_secret_placeholder'] = encrypted_api_secret_placeholder

        try:
            setting, created = MarketplaceIntegrationSettings.objects.update_or_create(
                owner_identifier=owner_id,
                marketplace_name=marketplace_name,
                defaults=defaults_to_update
            )
            status_code = 201 if created else 200
            return JsonResponse({'message': 'Marketplace settings saved successfully', 'id': setting.pk}, status=status_code)
        except Exception as e:
            return JsonResponse({'error': f'Error saving marketplace settings: {str(e)}'}, status=500)

class IssueTrackingSettingsView(View):
    async def get(self, request, *args, **kwargs):
        owner_id = request.GET.get('owner_identifier')
        integration_name = request.GET.get('integration_name')

        if not owner_id:
            return JsonResponse({'error': 'Owner identifier (owner_identifier) missing in query parameters'}, status=400)
        if not integration_name:
            return JsonResponse({'error': 'Integration name (integration_name) missing in query parameters'}, status=400)

        try:
            setting = IssueTrackingSystemSettings.objects.get(owner_identifier=owner_id, integration_name=integration_name)
            data_to_return = {
                'owner_identifier': setting.owner_identifier,
                'integration_name': setting.integration_name,
                'system_provider': setting.system_provider,
                'api_base_url': setting.api_base_url,
                'default_project_key': setting.default_project_key,
                'is_enabled': setting.is_enabled,
                'advanced_settings': setting.advanced_settings,
                'updated_at': setting.updated_at.isoformat()
            }
            return JsonResponse(data_to_return)
        except IssueTrackingSystemSettings.DoesNotExist:
            return JsonResponse({'error': 'Issue tracking system settings not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

        owner_id = data.get('owner_identifier')
        integration_name = data.get('integration_name')
        system_provider = data.get('system_provider')
        api_base_url = data.get('api_base_url')
        
        if not owner_id:
            return JsonResponse({'error': 'Missing required field: owner_identifier'}, status=400)
        if not integration_name:
            return JsonResponse({'error': 'Missing required field: integration_name'}, status=400)
        if not system_provider:
            return JsonResponse({'error': 'Missing required field: system_provider'}, status=400)
        if not api_base_url:
            return JsonResponse({'error': 'Missing required field: api_base_url'}, status=400)

        credentials_placeholder_data = data.get('credentials_placeholder', {})
        default_project_key = data.get('default_project_key')
        is_enabled = data.get('is_enabled', False)
        advanced_settings = data.get('advanced_settings', {})

        if not isinstance(credentials_placeholder_data, dict):
            return JsonResponse({'error': 'Invalid type for credentials_placeholder, JSON object expected'}, status=400)
        if not isinstance(is_enabled, bool):
            return JsonResponse({'error': 'Invalid type for is_enabled, boolean expected'}, status=400)
        if not isinstance(advanced_settings, dict):
            return JsonResponse({'error': 'Invalid type for advanced_settings, JSON object expected'}, status=400)

        encrypted_credentials_placeholder = {}
        if isinstance(credentials_placeholder_data, dict):
             for key, value in credentials_placeholder_data.items():
                 if isinstance(value, str):
                     encrypted_credentials_placeholder[key] = encrypt_value(value)
                 else:
                     encrypted_credentials_placeholder[key] = value # Zachowaj inne typy bez zmian, jeśli to konieczne
        else:
            encrypted_credentials_placeholder = {}


        defaults_to_update = {
            'system_provider': system_provider,
            'api_base_url': api_base_url,
            'credentials_placeholder': encrypted_credentials_placeholder,
            'default_project_key': default_project_key,
            'is_enabled': is_enabled,
            'advanced_settings': advanced_settings,
        }

        try:
            setting, created = IssueTrackingSystemSettings.objects.update_or_create(
                owner_identifier=owner_id,
                integration_name=integration_name,
                defaults=defaults_to_update
            )
            status_code = 201 if created else 200
            return JsonResponse({'message': 'Issue tracking system settings saved successfully', 'id': setting.pk}, status=status_code)
        except Exception as e:
            return JsonResponse({'error': f'Error saving issue tracking system settings: {str(e)}'}, status=500)
