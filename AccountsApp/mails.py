from django.contrib.auth.models import AbstractBaseUser

def send_email_verification_link(user: AbstractBaseUser, url: str):
    pass

def send_email_verification_code(user: AbstractBaseUser, code: str):
    pass

def send_password_reset_code(user: AbstractBaseUser, code: str):
    pass

def send_password_reset_link(user: AbstractBaseUser, url: str):
    pass