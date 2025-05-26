# /home/ubuntu/platform-services/integration_settings_service/encryption_utils.py
# Autor: Szymon Fuchs
# Data: 27.09.2021

def encrypt_value(value: str) -> str:
    if not value:
        return value

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value: # or not encrypted_value.startswith("encrypted__"):
        return encrypted_value
