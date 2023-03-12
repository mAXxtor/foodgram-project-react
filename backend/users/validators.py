import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """
    Regex валидация имени пользователя.
    """
    if not re.compile(r'[\w.@+-]+').fullmatch(username):
        restricted_symbols = re.compile(r'[\w.@+-]+').sub('', username)
        raise ValidationError(
            'Имя пользователя должно состоять из букв, цифр и '
            'символов ./@/+/-/_.'
            f'Использование {restricted_symbols} недопоступимо.')
    return username
