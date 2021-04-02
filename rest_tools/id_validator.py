import re

from rest_framework.serializers import ValidationError

def id_validator(value):
    pattern = re.compile('^[0-9a-zA-Z_]{6,20}$')
    if not pattern.search(value):
        raise ValidationError('id必须是字母，数字或下划线')
