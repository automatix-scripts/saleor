# /home/ubuntu/platform-services/monitoring_service/alerting/base_notifier.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from abc import ABC, abstractmethod

class BaseAlertNotifier(ABC):
    def __init__(self, channel_configuration):
        self.config = channel_configuration

    @abstractmethod
    def send_alert(self, subject, message, details_dict):
        pass
