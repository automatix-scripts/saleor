# /home/ubuntu/platform-services/monitoring_service/alerting/email_notifier.py
# Autor: Szymon Fuchs
# Data: 05.10.2021

from .base_notifier import BaseAlertNotifier

class EmailAlertNotifier(BaseAlertNotifier):
    def send_alert(self, subject, message, details_dict):
        email_to = self.config.get('email_to', [])
        if not email_to:
            print("Error: Email recipient not configured.")
            return False
        
        full_message = f"{message}\n\nDetails:\n"
        for key, value in details_dict.items():
            full_message += f"- {key}: {value}\n"

        print(f"Placeholder: Sending email to {email_to} with subject '{subject}' and message:\n{full_message}")
        return True
