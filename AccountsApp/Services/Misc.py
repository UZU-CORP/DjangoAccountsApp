from AccountsApp.exceptions import exception_filter_decor
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from posixpath import join as urljoin
from urllib.parse import urlencode

User =  get_user_model()
UsernameField: str = User.USERNAME_FIELD
EmailField: str = User.EMAIL_FIELD

@exception_filter_decor
def resolve_user(request: Request):
    user: AbstractBaseUser
    if request.user.is_authenticated:
        user = request.user
        return user
    query = resolve_user_query(request)
    user = User.objects.get(**query)
    return user

def resolve_user_query(request: Request):
    username, value = get_username_field(request)
    return {username: value}

@exception_filter_decor
def get_username_field(request: Request):
    if request.data.get(UsernameField, None):
        return UsernameField, request.data.get(UsernameField)
    elif request.data.get(EmailField, None):
        return EmailField, request.data.get(EmailField)
    else:
        raise ValidationError("{} or {} fields required".format(
            UsernameField, EmailField
        ) )

def build_secure_url(
    host: str, base_url: str, page_url: str,
    username_signature: str, code_signature: str
    ):
    url = urljoin(host, base_url, page_url)
    query = urlencode({"u": username_signature, 'c': code_signature })
    url = f'{url}?{query}'
    return url
        