import re

from django.core.exceptions import ValidationError


def national_code_validator(national_code):
    if len(national_code) != 10:
        raise ValidationError("Invalid National Code", code='invalid')
    try:
        int(national_code)
    except (TypeError, ValueError):
        raise ValidationError("Invalid National Code", code='invalid')
    not_national = list()
    for i in range(0, 10):
        not_national.append(str(i) * 10)
    if national_code in not_national:
        raise ValidationError("Invalid National Code", code='invalid')
    total = 0
    nc_p = nc[:9]
    i = 0
    for c in nc_p:
        total = total + int(c) * (10 - i)
        i = i + 1
    rem = total % 11
    if rem < 2:
        if int(national_code[9]) != rem:
            raise ValidationError("Invalid National Code", code='invalid')
    else:
        if int(national_code[9]) != 11 - rem:
            raise ValidationError("Invalid National Code", code='invalid')


def mobile_number_validator(mobile_number):
    if not re.match("09\\d{9}", mobile_number):
        raise ValidationError("Invalid Mobile Number", code='invalid')
