from typing import Set
from unittest import mock, TestCase
from django.conf import settings

from . import dummy_settings
from django.contrib.auth import get_user_model
from AccountsApp.Models.two_factor import EmailToken, OtpToken
from django.core.signing import SignatureExpired, Signer, TimestampSigner
from AccountsApp.utils.code_generator import generate_number_code
from faker import Faker
User = get_user_model()

class TestEmailToken(TestCase):

    def setUp(self):
        self.username = "Fakename"
        self.user = User(username=self.username)
    @mock.patch("django.db.models.Model.save")
    def test_get_code(self, save: mock.MagicMock):
        token = EmailToken(user=self.user)
        code, signature = token.get_code()
        code_length = settings.ACCOUNTS_APP['code_length']
        self.assertEqual(len(code), code_length)
        self.assertEqual(signature, TimestampSigner().sign(self.username))
    
    @mock.patch("django.core.signing.TimestampSigner.unsign")
    @mock.patch("django.db.models.Model.save")
    def test_token_invalid_if_signature_expires(self, save, unsign):
        unsign.side_effect = SignatureExpired
        token = EmailToken(user=self.user)
        is_valid = token.is_valid("2937398")
        self.assertFalse(is_valid)
    
    @mock.patch("django.core.signing.TimestampSigner.unsign")
    @mock.patch("django.db.models.Model.save")
    def test_token_validated_by_code_if_signature_valid(self, save, unsign):
        code = "2937398"
        token = EmailToken(user=self.user, code=code)
        is_valid = token.is_valid(code)
        self.assertTrue(is_valid)
        token.code = "373873"
        is_valid = token.is_valid(code)
        self.assertFalse(is_valid)


class TestOtpToken(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.username = "Fakename"
        self.user = User(username=self.username)
    
    @mock.patch("django.db.models.Model.save")
    def test_get_code(self, save: mock.MagicMock):
        token = OtpToken(user=self.user)
        _, signature = token.get_code()
        test_signature =  Signer().sign(self.username)
        self.assertEqual(test_signature, signature)
        
    @mock.patch("pyotp.totp.TOTP.verify")
    @mock.patch("django.db.models.Model.save")
    def test_token_invalid_if_otp_expires(self, save, verifier):
        verifier.return_value = False
        token = OtpToken(user=self.user, signature="empty")
        is_valid = token.is_valid("2937398")
        self.assertFalse(is_valid)


    @mock.patch("pyotp.totp.TOTP.verify")
    @mock.patch("django.db.models.Model.save")
    def test_token_validated_by_code_if_otp_valid(self, save, verifier):
        verifier.return_value = True
        token = OtpToken(user=self.user, signature="empty")
        is_valid = token.is_valid("897977")
        self.assertTrue(is_valid)
        verifier.return_value = True
        is_valid = token.is_valid("897977")
        self.assertFalse(is_valid)
    
    @mock.patch("pyotp.totp.TOTP.verify")
    @mock.patch("django.db.models.Model.save")
    def test_token_cannot_be_reused(self, save, verifier):
        code = "897977"
        verifier.return_value = True
        token = OtpToken(user=self.user, signature="empty")
        is_valid = token.is_valid(code)
        self.assertTrue(is_valid)
        is_valid = token.is_valid(code)
        self.assertFalse(is_valid)
    
    @mock.patch("pyotp.totp.TOTP.verify")
    @mock.patch("django.db.models.Model.save")
    def test_used_codes_truncated_when_too_long(self, save, verifier):
        verifier.return_value = True
        token = OtpToken(user=self.user, signature="empty")
        token_range = 10
        for _ in range(token_range):
            code = self.faker.unique.random_number(4)
            token.is_valid(str(code))
        used_codes = token.used_codes
        used_code_list = used_codes.split("+")
        self.assertEqual(len(used_code_list), token_range)
        token.save()
        used_codes = token.used_codes
        used_code_list = used_codes.split("+")
        self.assertLess(len(used_code_list), token_range)