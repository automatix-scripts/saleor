# /home/ubuntu/platform-services/company_data_service/views.py
# Autor: Szymon Fuchs
# Data: 23.08.2021

from django.http import JsonResponse
from django.views import View
import json
from .validators import is_valid_nip, is_valid_regon

class ValidateCompanyIdentifiersView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            nip = data.get('nip')
            regon = data.get('regon')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        errors = {}
        if nip and not is_valid_nip(nip):
            errors['nip'] = 'Invalid NIP format or checksum.'
        if regon and not is_valid_regon(regon):
            errors['regon'] = 'Invalid REGON format or checksum.'
            
        if errors:
            return JsonResponse({'valid': False, 'errors': errors}, status=400)
        
        return JsonResponse({'valid': True, 'message': 'Identifiers appear valid.'})
