from AccountsApp.mails import send_two_factor_token
from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Models import TwoFactorTokens

def send_token(user: AbstractBaseUser):
    token = user.two_factor_token
    code, signature = token.get_code()
    if token.provider == TwoFactorTokens.EMAIL:
        send_two_factor_token(user, code)
    return signature