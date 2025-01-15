"""Валидаторы."""
import re
from rest_framework.serializers import ValidationError


USERNAME_PATTERN = r'^[\w.@+-]+$'


def custom_validate_username(value):
    """Проверяет имя пользователя."""
    errors = []
    if value == 'me':
        errors.append(
            'Использование имени "me" в качестве username запрещено')
    if not re.match(USERNAME_PATTERN, value):
        errors.append(
            'Может содержать только буквы, цифры и символы @/./+/-/_')
    if errors:
        raise ValidationError(errors)
    return value
