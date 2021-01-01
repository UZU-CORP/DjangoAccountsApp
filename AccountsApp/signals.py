from django.conf import settings
from AccountsApp.Services.EmailVerificationService import EmailVerificationService
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.dispatch import Signal
from django.dispatch.dispatcher import receiver
from rest_framework.request import Request
from threading import Thread
from AccountsApp.constants import EMAIL_VERIF_URL

SignedUp = Signal(providing_args=["user", "request"])

@receiver(SignedUp)
def sign_up_handler(sender, **kwargs):
    request: Request = kwargs['request']
    user: AbstractBaseUser = kwargs['user']
    base_url = settings.ACCOUNTS_APP['base_url']
    service = EmailVerificationService(user, base_url)
    Thread(
        target=service.send_verification_link, 
        args=["https://" + request.META["HTTP_HOST"], EMAIL_VERIF_URL]
    ).start()