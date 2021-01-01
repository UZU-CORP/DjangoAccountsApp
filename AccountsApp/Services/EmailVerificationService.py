from ..Models import Verification
from django.contrib.auth.models import AbstractBaseUser
from .Misc import build_secure_url
from AccountsApp.mails import send_email_verification_link, send_email_verification_code

class EmailVerificationService:
    user: AbstractBaseUser
    verification: Verification
    base_url: str
    
    def __init__(self, user: AbstractBaseUser, base_url: str):
        self.user = user
        self.base_url = base_url
        self.verification, _ = Verification.objects.get_or_create(user=user)

    def send_verification_code(self):
        send_email_verification_code(self.user, self.verification.code)
        
    def send_verification_link(self, http_host: str, base_url: str):
        url =  build_secure_url(
            http_host, self.base_url, base_url, 
            self.verification.username_signature, 
            self.verification.code_signature
        )
        send_email_verification_link(self.user, url)

