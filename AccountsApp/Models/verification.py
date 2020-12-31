from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from ..utils.code_generator import generate_number_code
from django.utils import timezone
from django.core.signing import TimestampSigner, SignatureExpired, Signer

User = get_user_model()

class Verification(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        related_name="verification"
    )
    code = models.CharField(max_length=settings.ACCOUNTS_APP["code_length"])
    username_signature = models.TextField(null=True)
    code_signature = models.TextField(null=True)
    verified = models.BooleanField(default=False)

    def set_usersignature(self):
        self.username_signature = Signer().signature(self.user.get_username())


    def set_code(self):
        self.code = generate_number_code(
            settings.ACCOUNTS_APP.get("code_length", 10)
        )

    def set_codesignature(self):
        self.code_signature = Signer().signature(self.code)

    def save(self, *args, **kwargs):
        self.code or self.set_code()
        self.username_signature or self.set_usersignature()
        self.code_signature or self.set_codesignature()
        super().save(*args, **kwargs)