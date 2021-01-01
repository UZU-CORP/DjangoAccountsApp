from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.fields import proxy
from AccountsApp.utils.code_generator import generate_number_code
from datetime import timedelta
from django.core.signing import BadSignature, TimestampSigner, SignatureExpired, Signer
from django.contrib.auth.base_user import AbstractBaseUser
from pyotp import totp, random_base32

User = get_user_model()



class TwoFactorTokens(models.Model):
    EMAIL = 'email'
    OTP = 'otp'

    choices = ((EMAIL, 'Email'), (OTP, "Otp"))

    provider = models.CharField(choices=choices)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        related_name="two_factor_token"
    )
    code = models.CharField(max_length=100, null=True)
    signature = models.TextField(null=True)


    @classmethod
    def Find(cls, provider: str, signature, code: str = None):
        if provider == cls.OTP:
            return OtpToken.Find(signature=signature)
        else:
            return EmailToken.Find(signature=signature, code=code)


    @classmethod
    def SetUp(cls, user: AbstractBaseUser, provider: str):
        if provider == cls.OTP:
            return OtpToken.SetUp(user=user)
        else:
            return EmailToken.SetUp(user=user)

class EmailToken(TwoFactorTokens):

    class Meta:
        proxy = True

    @classmethod
    def Find(cls, signature, code):
        return cls.objects.get(
            models.Q(signature=signature) & models.Q(code=code)
        )

    @classmethod
    def SetUp(cls, user: AbstractBaseUser):
        token, _ = cls.objects.get_or_create(user=user)
        token.provider = cls.EMAIL
        return ""

    def get_code(self):
        self.__generate_data()
        return self.code, self.signature

    def __generate_data(self):
        code_length = int(settings.ACCOUNTS_APP["code_length"])
        self.signature = TimestampSigner().sign(self.user.get_username())
        self.code = generate_number_code(code_length)

    def is_valid(self, code: str):
        duration = settings.ACCOUNTS_APP["2fa_duration"]
        max_age = timedelta(minutes=duration)
        try:
            TimestampSigner().unsign(self.signature, max_age=max_age)
        except SignatureExpired:
            return False
        else:
            return code == self.code

class OtpToken(TwoFactorTokens):

    class Meta:
        proxy = True
        
    @classmethod
    def SetUp(cls, user: AbstractBaseUser):
        token, _ = cls.objects.get_or_create(user=user)
        token.provider = cls.OTP
        token.signature = random_base32()
        token.save()
        timed_otp = totp.TOTP(token.signature)
        return timed_otp.provisioning_uri(
            name=user.get_username(), issuer_name=settings.APP_NAME or ""
        )
    @classmethod
    def Find(cls, signature, *args, **kwargs):
        username_field = "user__%s".format(User.USERNAME_FIELD)
        try:
            username = Signer().unsign(signature)
        except BadSignature:
            raise cls.DoesNotExist()
        else:
            return cls.objects.get(**{username_field:username})

    @property
    def used_codes(self)-> str:
        return self.code or ""
    
    @used_codes.setter
    def used_codes(self, code: str):
        used = self.used_codes
        self.code = f'{used}+{code}' if used else code
    
    @property
    def user_signature(self):
        username = self.user.get_username()
        return Signer().sign(username)

    def __truncate_used_codes(self):
        used = self.used_codes
        if used.count("+") <= 5:
            return
        codes = used.split('+')
        fifth_to_last = len(codes) - 5
        codes = codes[fifth_to_last:]
        self.code = "+".join(codes)

    def get_code(self):
        return None, self.user_signature

    def save(self, *args, **kwargs):
        self.__truncate_used_codes()
        super().save(*args, **kwargs)

    def is_valid(self, code: str):
        if self.used_codes.find(code) >= 0:
            return False
        valid =  totp.TOTP(self.signature).verify(otp=code, valid_window=2)
        self.used_codes = code
        return valid
