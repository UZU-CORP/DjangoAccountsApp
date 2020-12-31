from AccountsApp.Models import verification
from ..Models import Verification, PasswordReset, TwoFactorTokens
from typing import Any, Dict
from django.contrib.auth.base_user import AbstractBaseUser


def verify_email_code(user_query: Dict[str, Any], code: str):
    verification: Verification = Verification.objects.get(
        code=code,
        **user_query
    )
    verification.verified = True
    verification.save()

def verify_email_link(username_sig: str, code_sig: int, ):
    verification: Verification = Verification.objects.get(
        username_signature=username_sig,
        code_signature=code_sig
    )
    verification.verified = True
    verification.save()


def verify_password_reset(code: str, signature: str):
    reset = PasswordReset.objects.get(code=code, signature=signature)
    if reset.is_expired():
        reset.delete()
        raise Exception("Password reset expired try again")
    user: AbstractBaseUser = reset.user
    reset.delete()
    return user

def verify_2fa_token(provider: str, code: str, signature: str):
    token = TwoFactorTokens.Find(provider, signature=signature, code=code)
    if token.is_valid():
       user: AbstractBaseUser = token.user
       return user
    else:
        raise Exception("Token Expired")

