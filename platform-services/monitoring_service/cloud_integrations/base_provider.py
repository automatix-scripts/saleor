# /home/ubuntu/platform-services/monitoring_service/cloud_integrations/base_provider.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from abc import ABC, abstractmethod

class BaseCloudMetricsProvider(ABC):
    def __init__(self, provider_settings):
        self.provider_settings = provider_settings

    @abstractmethod
    def get_metrics(self, resource_cloud_identifier, metric_definitions):
        pass

    @abstractmethod
    def test_connection(self):
        pass
