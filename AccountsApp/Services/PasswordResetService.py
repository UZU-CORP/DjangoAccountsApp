from AccountsApp.mails import send_password_reset_code, send_password_reset_link
from AccountsApp.Models.password_reset import PasswordReset
from typing import Dict, Any
from .Misc import build_secure_url


def __fetch_reset(user_query: Dict[str, Any]):
    query = {f"user__{key}": value for key,value in user_query.items()}
    reset, _ = PasswordReset.objects.get_or_create(**query)
    return reset

def send_reset_code(user_query: Dict[str, Any]):
    reset = __fetch_reset(user_query)
    code, signature = reset.get_data()
    send_password_reset_code(reset.user, code)
    return signature

def send_reset_link(
    user_query: Dict[str, Any], http_host: str, 
    base_url: str, page_url: str
):
    reset = __fetch_reset(user_query)
    code, signature = reset.get_data()
    url = build_secure_url(http_host, base_url, page_url, signature, code)
    send_password_reset_link(reset.user, url)
