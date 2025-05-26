# /home/ubuntu/platform-services/gus_integration_service/gus_client.py
# Autor: Szymon Fuchs
# Data: 01.09.2021

import requests
import xml.etree.ElementTree as ET
from django.conf import settings

GUS_API_BASE_URL = "https://WyszukiwaniePodmiotowWRegon.stat.gov.pl/wsBIR/UslugaBIRzewnPubl.svc"
GUS_API_TEST_URL = "https://WyszukiwaniePodmiotowWRegon.stat.gov.pl/wsBIRtest/UslugaBIRzewnPubl.svc"

GUS_API_ACTIONS_NS_MAP = {
    "Zaloguj": "http://CIS.BIR.PUBL.APL.CIS01.UslugaBIRzewnPubl.Contracts/IUslugaBIRzewnPubl/Zaloguj",
    "DaneSzukajPodmioty": "http://CIS.BIR.PUBL.APL.CIS01.UslugaBIRzewnPubl.Contracts/IUslugaBIRzewnPubl/DaneSzukajPodmioty",
    "Wyloguj": "http://CIS.BIR.PUBL.APL.CIS01.UslugaBIRzewnPubl.Contracts/IUslugaBIRzewnPubl/Wyloguj"
}
# Przestrzeń nazw dla elementów wewnątrz pParametryWyszukiwania
DAT_NS = "http://CIS.BIR. Віншую. ParametryPrzesylki"


class GUSApiClient:
    def __init__(self, api_key=None, test_mode=True):
        self.api_key = api_key or getattr(settings, 'GUS_USER_KEY', 'abcde12345abcde12345')
        self.base_url = GUS_API_TEST_URL if test_mode else GUS_API_BASE_URL
        self.session_id = None

    def _make_soap_request(self, action_name, soap_body_content_xml_str):
        action_url = GUS_API_ACTIONS_NS_MAP[action_name]
        
        soap_envelope = f"""<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:ns="{action_url}">
   <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
      <wsa:Action>{action_url}</wsa:Action>
      <wsa:To>{self.base_url}</wsa:To>
   </soap:Header>
   <soap:Body>
      {soap_body_content_xml_str}
   </soap:Body>
</soap:Envelope>"""
        
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-utf-8',
        }
        if self.session_id: # SID jest przekazywany w nagłówku HTTP dla kolejnych żądań
             headers['sid'] = self.session_id
        
        try:
            response = requests.post(self.base_url, data=soap_envelope.encode('utf-8'), headers=headers, timeout=15)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"GUS API request error ({action_name}): {e}")
            return None

    def login(self):
        body_content = f"<ns:Zaloguj><ns:pKluczUzytkownika>{self.api_key}</ns:pKluczUzytkownika></ns:Zaloguj>"
        response_xml = self._make_soap_request("Zaloguj", body_content)
        
        if response_xml:
            root = ET.fromstring(response_xml)
            # Ścieżki są specyficzne dla struktury odpowiedzi GUS
            ns_resp = {'bir': 'http://CIS.BIR.PUBL.APL.CIS01.UslugaBIRzewnPubl.Contracts'}
            sid_element = root.find('.//bir:ZalogujResult', namespaces=ns_resp)
            if sid_element is not None and sid_element.text:
                self.session_id = sid_element.text
                print(f"GUS login successful, SID: {self.session_id}")
                return True
        print("GUS login failed.")
        return False

    def logout(self):
        if not self.session_id:
            return True
        body_content = f"<ns:Wyloguj><ns:pIdentyfikatorSesji>{self.session_id}</ns:pIdentyfikatorSesji></ns:Wyloguj>"
        self._make_soap_request("Wyloguj", body_content)
        print(f"GUS logout attempted for SID: {self.session_id}")
        self.session_id = None
        return True

    def search_by_nip(self, nip):
        if not self.session_id:
            if not self.login():
                return None
        
        # Prawidłowa struktura XML dla pParametryWyszukiwania
        # Namespace 'dat' musi być zdefiniowany w Envelope lub tutaj
        # Poniżej uproszczona struktura, może wymagać korekty
        search_params_xml = f"""<ns0:DaneSzukajPodmioty xmlns:ns0="{GUS_API_ACTIONS_NS_MAP['DaneSzukajPodmioty']}">
    <ns0:pParametryWyszukiwania>
        <dat:Nip xmlns:dat="{DAT_NS}">{nip}</dat:Nip>
    </ns0:pParametryWyszukiwania>
</ns0:DaneSzukajPodmioty>"""
        
        response_xml = self._make_soap_request("DaneSzukajPodmioty", search_params_xml)
        
        if response_xml:
            print(f"GUS search response: {response_xml.decode('utf-8')[:500]}") # Log part of response
            root = ET.fromstring(response_xml)
            ns_resp = {'bir': 'http://CIS.BIR.PUBL.APL.CIS01.UslugaBIRzewnPubl.Contracts'}
            data_element = root.find('.//bir:DaneSzukajPodmiotyResult', namespaces=ns_resp)
            
            if data_element is not None and data_element.text:
                # Dane są zwracane jako string XML, który trzeba dalej sparsować
                company_data_xml_str = data_element.text
                print(f"GUS company data XML string: {company_data_xml_str[:500]}")
                # Tutaj implementacja parsowania tego XML stringu
                # Przykład:
                # company_root = ET.fromstring(company_data_xml_str)
                # Należy znaleźć odpowiednie tagi, np. Nazwa, Ulica, Miasto etc.
                # nazwa = company_root.find('.//Nazwa').text if company_root.find('.//Nazwa') is not None else 'Brak danych'
                # return {'nazwa': nazwa, 'regon': company_root.find('.//Regon').text ...}
                # Zwracamy surowy string XML do dalszego parsowania lub pusty słownik
                return {"raw_xml_data": company_data_xml_str} 
        
        return None

    def __enter__(self):
        # self.login() # Logowanie lepiej robić przed konkretnym zapytaniem
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
