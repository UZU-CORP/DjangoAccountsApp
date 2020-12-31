from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Services.EmailVerificationService import EmailVerificationService
from unittest import TestCase, mock
from faker import Faker
from AccountsApp.Models import Verification

class TestEmailVerificationService(TestCase):
    def setUp(self):
        self.faker = Faker()
    
    @mock.patch("AccountsApp.Models.Verification.objects.get_or_create")
    @mock.patch("AccountsApp.Services.EmailVerificationService.send_email_verification_code")
    def test_send_verification_code(self, mailer: mock.MagicMock, get_or_create):
        user = mock.MagicMock(spec=AbstractBaseUser)
        verification = mock.MagicMock(spec=Verification)
        verification.code = str( self.faker.random_number(4) )
        get_or_create.return_value = verification, True
        service = EmailVerificationService(user, self.faker.url())
        service.send_verification_code()
        mailer.assert_called_once_with(user, verification.code)
    

    @mock.patch("AccountsApp.Models.Verification.objects.get_or_create")
    @mock.patch("AccountsApp.Services.EmailVerificationService.send_email_verification_link")
    def test_send_verification_code(self, mailer: mock.MagicMock, get_or_create):
        user = mock.MagicMock(spec=AbstractBaseUser)
        verification = mock.MagicMock(spec=Verification)
        verification.code = str( self.faker.random_number(4) )
        verification.username_signature = self.faker.sha1()
        verification.code_signature = self.faker.sha1()
        get_or_create.return_value = verification, True
        uri_path = self.faker.uri_path()
        service = EmailVerificationService(user, uri_path)
        service.send_verification_link(self.faker.url())
        mailer.assert_called_once()
    