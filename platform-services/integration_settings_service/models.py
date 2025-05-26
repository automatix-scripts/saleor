# /home/ubuntu/platform-services/integration_settings_service/models.py
# Autor: Szymon Fuchs
# Data: 27.09.2021

from django.db import models
from django.db.models import JSONField

class MarketplaceIntegrationSettings(models.Model):
    owner_identifier = models.CharField(max_length=255, help_text="Identyfikator właściciela (np. Saleor User ID lub Channel ID)")
    marketplace_name = models.CharField(max_length=100)
    api_key_placeholder = models.CharField(max_length=512, blank=True, null=True, help_text="Placeholder for API Key - DO NOT STORE PLAINTEXT; store encrypted or use Vault")
    api_secret_placeholder = models.CharField(max_length=512, blank=True, null=True, help_text="Placeholder for API Secret - DO NOT STORE PLAINTEXT; store encrypted or use Vault")
    is_active = models.BooleanField(default=False)
    sync_products_enabled = models.BooleanField(default=False, help_text="Czy synchronizować produkty?")
    sync_orders_enabled = models.BooleanField(default=False, help_text="Czy synchronizować zamówienia?")
    last_successful_sync = models.DateTimeField(null=True, blank=True)
    additional_config = JSONField(default=dict, blank=True, help_text="Dodatkowe ustawienia specyficzne dla marketplace w formacie JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner_identifier', 'marketplace_name')
        verbose_name = "Marketplace Integration Setting"
        verbose_name_plural = "Marketplace Integration Settings"

    def __str__(self):
        return f"Settings for {self.marketplace_name} / Owner: {self.owner_identifier}"

class IssueTrackingSystemSettings(models.Model):
    owner_identifier = models.CharField(max_length=255, help_text="Identyfikator właściciela (np. Saleor User ID lub Channel ID)")
    integration_name = models.CharField(max_length=100, help_text="Unikalna nazwa konfiguracji integracji systemu zgłoszeń")
    system_provider = models.CharField(max_length=50, help_text="Dostawca systemu zgłoszeń (np. JIRA, Zendesk, Custom)")
    api_base_url = models.URLField(max_length=512, help_text="Bazowy URL API systemu zgłoszeń")
    credentials_placeholder = JSONField(default=dict, blank=True, help_text="Placeholder dla danych uwierzytelniających (np. klucz API, token) - NIE PRZECHOWUJ W FORMIE TEKSTOWEJ; store encrypted or use Vault")
    default_project_key = models.CharField(max_length=100, blank=True, null=True, help_text="Domyślny klucz projektu lub identyfikator w systemie zgłoszeń")
    is_enabled = models.BooleanField(default=False, help_text="Czy integracja jest aktywna?")
    advanced_settings = JSONField(default=dict, blank=True, help_text="Dodatkowe ustawienia specyficzne dla systemu zgłoszeń w formacie JSON (np. mapowanie pól, typy zgłoszeń)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner_identifier', 'integration_name')
        verbose_name = "Issue Tracking System Setting"
        verbose_name_plural = "Issue Tracking System Settings"

    def __str__(self):
        return f"Issue Tracking Settings for {self.integration_name} ({self.system_provider}) / Owner: {self.owner_identifier}"
