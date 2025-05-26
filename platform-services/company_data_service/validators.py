# /home/ubuntu/platform-services/company_data_service/validators.py
# Autor: Szymon Fuchs
# Data: 23.08.2021

import re

def is_valid_nip(nip):
    if not isinstance(nip, str):
        return False
    nip = nip.replace('-', '').replace(' ', '')
    if not re.match(r'^\d{10}$', nip):
        return False
    
    weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    control_sum = sum(int(nip[i]) * weights[i] for i in range(9))
    control_digit = control_sum % 11
    
    return control_digit == int(nip[9])

def is_valid_regon(regon):
    if not isinstance(regon, str):
        return False
    regon = regon.replace('-', '').replace(' ', '')
    if not re.match(r'^\d{9}$|^\d{14}$', regon):
        return False
    if len(regon) == 9:
        weights = [8, 9, 2, 3, 4, 5, 6, 7]
        control_sum = sum(int(regon[i]) * weights[i] for i in range(8))
        control_digit = control_sum % 11
        if control_digit == 10: control_digit = 0
        return control_digit == int(regon[8])
    return True
