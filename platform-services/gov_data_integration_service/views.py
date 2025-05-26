# /home/ubuntu/platform-services/gov_data_integration_service/views.py
# Autor: Szymon Fuchs
# Data: 15.09.2021

from django.http import JsonResponse
from django.views import View
import json
from .ceidg_client import CeidgApiClient
from .krs_client import KrsApiClient

class CeidgDataView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            nip = data.get('nip')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not nip:
            return JsonResponse({'error': 'NIP not provided for CEIDG lookup'}, status=400)

        client = CeidgApiClient()
        company_data = client.get_company_data_by_nip(nip)

        if company_data and not company_data.get("error"):
            return JsonResponse(company_data)
        else:
            status_code = 404 if company_data and company_data.get("error") else 500
            return JsonResponse(company_data or {'error': 'Could not retrieve company data from CEIDG.'}, status=status_code)

class KrsDataView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            krs_number = data.get('krs_number')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not krs_number:
            return JsonResponse({'error': 'KRS number not provided for KRS lookup'}, status=400)

        client = KrsApiClient()
        company_data = client.get_company_data_by_krs_number(krs_number)

        if company_data and not company_data.get("error"):
            return JsonResponse(company_data)
        else:
            status_code = 404 if company_data and company_data.get("error") else 500
            return JsonResponse(company_data or {'error': 'Could not retrieve company data from KRS.'}, status=status_code)
