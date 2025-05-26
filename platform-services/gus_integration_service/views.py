# /home/ubuntu/platform-services/gus_integration_service/views.py
# Autor: Szymon Fuchs
# Data: 03.09.2021

from django.http import JsonResponse
from django.views import View
from .gus_client import GUSApiClient
import json

class GetCompanyDataByNipView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            nip = data.get('nip')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not nip:
            return JsonResponse({'error': 'NIP not provided'}, status=400)

        with GUSApiClient(test_mode=True) as client: # Użyj test_mode=False dla produkcji
            if not client.login(): # Jawne logowanie przed użyciem
                 return JsonResponse({'error': 'Failed to login to GUS API'}, status=503)
            company_data = client.search_by_nip(nip)

        if company_data and company_data.get("raw_xml_data"):
            # Tutaj można zaimplementować bardziej szczegółowe parsowanie XML
            # Zamiast zwracać surowy XML
            # Na przykład:
            # parsed_info = parse_gus_xml_response(company_data.get("raw_xml_data"))
            # return JsonResponse(parsed_info)
            return JsonResponse(company_data) 
        elif company_data: # Na wypadek gdyby search_by_nip zwracał już sparsowane dane
             return JsonResponse(company_data)
        else:
            return JsonResponse({'error': 'Could not retrieve company data from GUS or NIP not found.'}, status=404)
