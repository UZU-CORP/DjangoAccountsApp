from AccountsApp.Models.two_factor import TwoFactorTokens
from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Models.password_reset import PasswordReset
from AccountsApp.Models import verification
from unittest import TestCase, mock
from faker import Faker
from AccountsApp.Services.VerifierService import verify_2fa_token, verify_email_code, verify_email_link, verify_password_reset
class TestVerifierService(TestCase):
    def setUp(self):
        self.faker = Faker()
    
    @mock.patch("AccountsApp.Services.VerifierService.Verification.objects.get")
    def test_verify_email_code(self, get):
        user_query = {"user__id": self.faker.random_number(2)}
        code =  self.faker.random_number(4)
        verification = mock.Mock()
        verification.verified = False
        get.return_value = verification
        verify_email_code(user_query, code)
        get.assert_called_once_with(code=code, **user_query)
        verification.save.assert_called_once()
        self.assertTrue(verification.verified)
    
    @mock.patch("AccountsApp.Services.VerifierService.Verification.objects.get")
    def test_verify_email_link(self, get):
        username_sig = self.faker.sha1()
        code_sig = self.faker.sha1()
        verification = mock.Mock()
        verification.verified = False
        get.return_value = verification
        verify_email_link(username_sig, code_sig)
        get.assert_called_once_with(
            username_signature=username_sig,
            code_signature=code_sig
        )
        verification.save.assert_called_once()
        self.assertTrue(verification.verified)

    @mock.patch("AccountsApp.Services.VerifierService.PasswordReset.objects.get")
    def test_verify_password_reset(self, get):
        reset = mock.Mock(spec=PasswordReset)
        get.return_value = reset
        reset.is_expired.return_value = False        
        user = mock.Mock(spec=AbstractBaseUser)
        reset.user = user
        code = str( self.faker.random_number(8) )
        signature = self.faker.sha1()
        returned_user = verify_password_reset(code, signature)
        self.assertEqual(user, returned_user)
        reset.is_expired.assert_called_once()
        reset.delete.assert_called_once()
    
    @mock.patch("AccountsApp.Services.VerifierService.PasswordReset.objects.get")
    def test_verify_password_reset_raises_exception_on_expiry(self, get):
        reset = mock.Mock(spec=PasswordReset)
        get.return_value = reset
        reset.is_expired.return_value = True
        code = str( self.faker.random_number(8) )
        signature = self.faker.sha1()
        with self.assertRaises(Exception):
            verify_password_reset(code, signature)
        reset.is_expired.assert_called_once()
        reset.delete.assert_called_once()

    @mock.patch("AccountsApp.Services.VerifierService.TwoFactorTokens.Find")
    def test_verify_2fa(self, find):
        token = mock.Mock()
        find.return_value = token
        token.is_valid.return_value = True
        user = mock.Mock(spec=AbstractBaseUser)
        token.user = user
        code = str( self.faker.random_number(8) )
        signature = self.faker.sha1()
        returned_user = verify_2fa_token("mail", code, signature)
        self.assertEqual(returned_user, user)

    @mock.patch("AccountsApp.Services.VerifierService.TwoFactorTokens.Find")
    def test_verify_2fa_raises_exception_on_expiry(self, find):
        token = mock.Mock()
        find.return_value = token
        token.is_valid.return_value = False
        code = str( self.faker.random_number(8) )
        signature = self.faker.sha1()
        with self.assertRaises(Exception):
            verify_2fa_token("mail", code, signature)