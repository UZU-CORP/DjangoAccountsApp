from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from rest_framework.request import Request
from posixpath import join as urljoin

User =  get_user_model()
UsernameField: str = User.USERNAME_FIELD
EmailField: str = User.EMAIL_FIELD

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

def get_username_field(request: Request):
    if request.get(UsernameField, None):
        return UsernameField, request.data.get(UsernameField)
    elif request.get(EmailField, None):
        return EmailField, request.data.get(EmailField)
    else:
        raise User.DoesNotExist()

def build_secure_url(
    host: str, base_url: str, page_url: str,
    username_signature: str, code_signature: str
    ):
    url = urljoin(host, base_url, page_url)
    url = url + "?u=%s&c=%s".format(
        username_signature, 
        code_signature
    )
    return url
        