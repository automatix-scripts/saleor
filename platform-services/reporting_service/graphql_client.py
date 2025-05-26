# /home/ubuntu/platform-services/reporting_service/graphql_client.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

import httpx
from django.conf import settings
import json

SALEOR_GRAPHQL_URL = getattr(settings, 'SALEOR_GRAPHQL_URL', 'http://localhost:8000/graphql/')
SALEOR_APP_TOKEN = getattr(settings, 'SALEOR_APP_TOKEN', None)

class SaleorGraphQLClient:
    async def execute(self, query, variables=None):
        headers = {
            'Content-Type': 'application/json',
        }
        if SALEOR_APP_TOKEN:
            headers['Authorization'] = f'Bearer {SALEOR_APP_TOKEN}'

        payload = {'query': query}
        if variables:
            payload['variables'] = variables

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(SALEOR_GRAPHQL_URL, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_response_text = "No response text"
            try:
                error_response_text = e.response.text
            except Exception:
                pass
            return {'errors': [{'message': f'HTTP error: {e.response.status_code} - {error_response_text}'}]}
        except httpx.RequestError as e:
            return {'errors': [{'message': f'Request error: {str(e)}'}]}
        except json.JSONDecodeError:
            return {'errors': [{'message': 'Invalid JSON response from Saleor API'}]}
