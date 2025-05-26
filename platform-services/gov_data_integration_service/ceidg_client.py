# /home/ubuntu/platform-services/gov_data_integration_service/ceidg_client.py
# Autor: Szymon Fuchs
# Data: 10.09.2021

import requests
from django.conf import settings
# Dla SOAP, biblioteka zeep byłaby standardem w 2021
# from zeep import Client as ZeepClient
# from zeep.transports import Transport as ZeepTransport
# from requests import Session as RequestsSession

# WSDL_URL_CEIDG_PROD = getattr(settings, 'CEIDG_WSDL_URL', 'https_URL_PRODUKCYJNY_WSDL_CEIDG_Z_2021')
# CEIDG_API_USER_KEY = getattr(settings, 'CEIDG_API_USER_KEY', None) # Klucz użytkownika dla API CEIDG

class CeidgApiClient:
    def __init__(self, wsdl_url=None, api_user_key=None, test_mode=True):
        # self.wsdl_url = wsdl_url if wsdl_url else WSDL_URL_CEIDG_PROD
        # self.api_user_key = api_user_key if api_user_key else CEIDG_API_USER_KEY
        # self.test_mode = test_mode # API CEIDG mogło mieć osobny endpoint testowy
        #
        # if self.wsdl_url and self.api_user_key:
        #     try:
        #         req_session = RequestsSession()
        #         # Tutaj mogłaby być dodatkowa konfiguracja sesji, np. nagłówki autoryzacyjne
        #         # req_session.headers.update({'ApiKey': self.api_user_key})
        #         zeep_transport = ZeepTransport(session=req_session, timeout=15)
        #         self.soap_client = ZeepClient(self.wsdl_url, transport=zeep_transport)
        #         print(f"CEIDG SOAP Client initialized for WSDL: {self.wsdl_url}")
        #     except Exception as e:
        #         print(f"Failed to initialize CEIDG SOAP Client: {e}")
        #         self.soap_client = None
        # else:
        #     self.soap_client = None
        #     print("CEIDG WSDL URL or API User Key not configured. Client not initialized.")
        print("CEIDG Client (conceptual) initialized.")


    def get_company_data_by_nip(self, nip):
        # if not self.soap_client:
        #     return {"error": "CEIDG client not initialized"}
        #
        # try:
        #     # Struktura zapytania i nazwa metody zależą od WSDL API CEIDG
        #     # Np. api_params = {'Auth': {'UserKey': self.api_user_key}, 'Nip': nip}
        #     # response = self.soap_client.service.DanePobierzPelnyRaport(Nip=nip) # lub bardziej złożone parametry
        #
        #     # Parsowanie odpowiedzi SOAP (obiekt Pythonowy z zeep)
        #     # company_name = response.DanePodmiotu.NazwaPelna
        #     # address_street = response.DanePodmiotu.AdresDzialalnosci.Ulica
        #     # ... itp.
        #     # return {
        #     #     "nazwa_firmy": company_name,
        #     #     "adres_glowny": f"{address_street} ...",
        #     #     "status": response.DanePodmiotu.Status,
        #     # }
        # except Exception as e:
        #     print(f"CEIDG SOAP API request error for NIP {nip}: {e}")
        #     return {"error": f"CEIDG API error: {e}"}

        if nip == "1112223344":
            return {
                "source": "CEIDG (Symulacja)",
                "nazwa_firmy": "Firma Testowa CEIDG Jan Kowalski",
                "adres_glowny": "ul. Słoneczna 1, 00-001 Warszawa",
                "status": "Aktywny",
                "data_rozpoczecia": "2010-01-01",
                "pkd_glowne": "12.34.Z"
            }
        return {"error": "Data not found or NIP invalid (simulation)"}
