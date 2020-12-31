from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Models.password_reset import PasswordReset
from unittest import TestCase, mock
from AccountsApp.Services import PasswordResetService
from faker import Faker

class TestPasswordResetService(TestCase):
    def setUp(self):
        self.faker = Faker()

    @mock.patch("AccountsApp.Services.PasswordResetService.send_password_reset_code")
    @mock.patch("AccountsApp.Services.PasswordResetService.PasswordReset.objects")
    def test_send_password_reset_code(self, manager: mock.MagicMock, mailer):
        reset  = mock.MagicMock(spec=PasswordReset)
        code = self.faker.random_number(4)
        signature = self.faker.sha1()
        reset.get_data.return_value = code, signature
        reset.user = mock.MagicMock(spec=AbstractBaseUser)
        reset.is_expired.return_value = False
        manager.get_or_create.return_value = reset, True
        returned_signature = PasswordResetService.send_reset_code({"id": 1})
        self.assertEqual(signature, returned_signature)
        mailer.assert_called_once_with(reset.user, code)
    

    @mock.patch("AccountsApp.Services.PasswordResetService.build_secure_url")
    @mock.patch("AccountsApp.Services.PasswordResetService.send_password_reset_link")
    @mock.patch("AccountsApp.Services.PasswordResetService.PasswordReset.objects")
    def test_send_password_reset_link(self, manager: mock.MagicMock, mailer, builder):
        reset  = mock.MagicMock(spec=PasswordReset)
        code = self.faker.random_number(4)
        signature = self.faker.sha1()
        reset.get_data.return_value = code, signature
        reset.user = mock.MagicMock(spec=AbstractBaseUser)
        reset.is_expired.return_value = False
        manager.get_or_create.return_value = reset, False
        url = self.faker.url()
        builder.return_value = url
        host = self.faker.url()
        base = "/accounts"
        page = "reset-password"
        PasswordResetService.send_reset_link({"id": 1}, host, base, page)
        mailer.assert_called_once_with(reset.user, url)