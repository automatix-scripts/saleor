# /home/ubuntu/platform-services/gov_data_integration_service/krs_client.py
# Autor: Szymon Fuchs
# Data: 12.09.2021

import requests
from django.conf import settings

# KRS_PROVIDER_API_URL = getattr(settings, 'KRS_PROVIDER_API_URL', 'https://api.example-krs-provider.com/v1')
# KRS_PROVIDER_API_KEY = getattr(settings, 'KRS_PROVIDER_API_KEY', 'your_krs_provider_api_key')

class KrsApiClient:
    def __init__(self, api_key=None, base_url=None):
        # self.api_key = api_key or KRS_PROVIDER_API_KEY
        # self.base_url = base_url or KRS_PROVIDER_API_URL
        # print(f"KRS Client initialized for URL: {self.base_url} (using commercial provider API concept)")
        print("KRS Client (conceptual for commercial provider API) initialized.")


    def get_company_data_by_krs_number(self, krs_number):
        # headers = {'X-Api-Key': self.api_key, 'Accept': 'application/json'}
        # endpoint = f"{self.base_url}/podmioty?numerKRS={krs_number}"
        # try:
        #     response = requests.get(endpoint, headers=headers, timeout=10)
        #     response.raise_for_status()
        #     data = response.json() # Zakładamy, że API dostawcy zwraca JSON
        #     return self._parse_krs_data(data)
        # except requests.exceptions.RequestException as e:
        #     print(f"KRS Provider API request error for KRS {krs_number}: {e}")
        #     return {"error": f"KRS Provider API error: {e}"}
        # except ValueError:
        #     print(f"KRS Provider API JSON parsing error for KRS {krs_number}")
        #     return {"error": "KRS Provider API parsing error"}
        
        if krs_number == "0000123456":
            return {
                "source": "KRS (Symulacja - API Dostawcy)",
                "nazwa_firmy": "Spółka Akcyjna Test KRS",
                "forma_prawna": "Spółka Akcyjna",
                "adres_siedziby": "ul. Korporacyjna 100, 02-200 Kraków",
                "nip": "9876543210",
                "regon": "987654321",
                "data_rejestracji": "2005-05-05"
            }
        return {"error": "Data not found or KRS number invalid (simulation)"}
    
    def _parse_krs_data(self, raw_data):
        # Logika mapowania pól z odpowiedzi API dostawcy KRS
        # Przykład:
        # if isinstance(raw_data, list) and len(raw_data) > 0:
        #    entity_data = raw_data[0] # Zakładamy, że API zwraca listę, bierzemy pierwszy element
        #    return {
        #         "nazwa_firmy": entity_data.get("nazwa"),
        #         "forma_prawna": entity_data.get("formaPrawna"),
        #         # ... inne pola
        #    }
        # return {"error": "No data found in KRS provider response"}
        return raw_data
