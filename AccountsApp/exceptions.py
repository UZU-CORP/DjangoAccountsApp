from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException, NotFound
from rest_framework.settings import APISettings

class TokenExpired(APIException):
    status_code = 401
    default_detail = " Token or link expired"
    default_code = "Expired"

def exception_filter_decor(func):
    def decor(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ObjectDoesNotExist as e:
            raise NotFound(e.args)
    return decor