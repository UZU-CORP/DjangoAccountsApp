from . import dummy_settings
from django.contrib.auth import get_user_model
from AccountsApp.Models import PasswordReset
from unittest import mock, TestCase
from django.core.signing import SignatureExpired, TimestampSigner
from django.conf import settings

User = get_user_model()

class TestPasswordResetModel(TestCase):

    @mock.patch("django.db.models.Model.save")
    def test_model_generates_data_on_save(self, save):
        username = "Fakename"
        userMock = User(username=username)
        password_reset = PasswordReset(user=userMock)
        password_reset.save()
        signed_username = TimestampSigner().sign(username)
        self.assertEqual(signed_username, password_reset.signature)
        code_length =  settings.ACCOUNTS_APP['code_length']
        self.assertEqual(code_length, password_reset.code_length)
    
    @mock.patch("django.core.signing.TimestampSigner.unsign")
    @mock.patch("django.db.models.Model.save")
    def test_is_expired_when_signature_expires(self, save, unsign):
        unsign.side_effect = SignatureExpired
        username = "Fakename"
        userMock = User(username=username)
        password_reset = PasswordReset(user=userMock)
        password_reset.save()
        is_expired = password_reset.is_expired()
        self.assertTrue(is_expired)
    
    @mock.patch("django.core.signing.TimestampSigner.unsign")
    @mock.patch("django.db.models.Model.save")
    def test_is_valid_when_signature_valid(self, save, unsign):
        username = "Fakename"
        userMock = User(username=username)
        password_reset = PasswordReset(user=userMock)
        password_reset.save()
        is_expired = password_reset.is_expired()
        self.assertFalse(is_expired)