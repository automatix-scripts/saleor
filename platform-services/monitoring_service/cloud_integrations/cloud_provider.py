# /home/ubuntu/platform-services/monitoring_service/cloud_integrations/aws_provider.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from .base_provider import BaseCloudMetricsProvider

class CloudMetricsProvider(BaseCloudMetricsProvider):
    def get_metrics(self, resource_cloud_identifier, metric_definitions_map):
        print(f"Placeholder: Fetching Cloud metrics for {resource_cloud_identifier} with {metric_definitions_map}")
        return []

    def test_connection(self):
        print(f"Placeholder: Testing Cloud connection with settings: {self.provider_settings.provider_name}")
        return True, "Placeholder: Cloud Connection OK"
