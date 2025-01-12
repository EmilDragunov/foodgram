import re
from rest_framework.serializers import ValidationError


PATTERN = r'^[\w.@+-]+$'


def validate_username(value):
    errors = []
    if value == 'me':
        errors.append(
            'Использовать имя "me" в качестве username запрещено')
    if not re.match(PATTERN, value):
        errors.append(
            'Может содержать только буквы, цифры и символы @/./+/-/_')
    if errors:
        raise ValidationError(errors)
    return value
