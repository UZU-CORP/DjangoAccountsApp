from django.http import response
from AccountsApp.Services import VerifierService
import json
from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Controllers import AuthController
from unittest import mock, TestCase
from faker import Faker
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate


class TestAuthenticationController(TestCase):
    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.controller: AuthController = AuthController.get_instance()
    
    @mock.patch("AccountsApp.Controllers.auth_controller.SignedUp")
    @mock.patch("AccountsApp.Controllers.auth_controller.User")
    @mock.patch("AccountsApp.Controllers.auth_controller.login")
    def test_signup(self, login, User, signal):
        user = mock.MagicMock(spec=AbstractBaseUser)
        User.return_value = user
        data = {
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "password": self.faker.first_name()
        }
        request = self.factory.post('signup', data)
        force_authenticate(request)
        request.session = mock.MagicMock()
        response = self.controller.signup(request)
        password = data.pop("password")
        User.assert_called_with(**data)
        signal.send.assert_called_once()
        user.set_password.assert_called_once_with(password)
        login.assert_called_once()
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])

    @mock.patch("AccountsApp.Controllers.auth_controller.User")
    @mock.patch("AccountsApp.Controllers.auth_controller.login")
    @mock.patch("AccountsApp.Controllers.auth_controller.authenticate")
    def test_signin_without_two_fa(self, authenticate, login, User):
        user = mock.MagicMock(spec=AbstractBaseUser)
        User.USERNAME_FIELD = "username"
        data = {
            "username": self.faker.first_name(),
            "password": self.faker.word()
        }
        authenticate.return_value = user
        request = self.factory.post('signin', data)
        response = self.controller.signin(request)
        authenticate.assert_called_with(**data)
        login.assert_called_once()
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
    
    @mock.patch("AccountsApp.Controllers.auth_controller.TwoFactorService")
    @mock.patch("AccountsApp.Controllers.auth_controller.User")
    @mock.patch("AccountsApp.Controllers.auth_controller.authenticate")
    def test_signin_with_two_fa(self, authenticate, User, two_fa_service):
        user = mock.MagicMock(spec=AbstractBaseUser)
        User.USERNAME_FIELD = "username"
        user.two_factor_enabled = True
        data = {
            "username": self.faker.first_name(),
            "password": self.faker.word()
        }
        signature =  self.faker.sha1()
        two_fa_service.send_token.return_value = signature
        authenticate.return_value = user
        request = self.factory.post('signin', data)
        response = self.controller.signin(request)
        authenticate.assert_called_with(**data)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        self.assertEqual(response_data["data"]["signature"], signature)
        

    def test_authenticate_success_with_right_password(self):
        password = self.faker.word()
        data = {"password": password}
        request = self.factory.post('authenticate', data)
        user =  mock.MagicMock(spec=AbstractBaseUser)
        user.check_password.return_value = True
        force_authenticate(request, user)
        response = self.controller.authenticate(request)
        user.check_password.assert_called_with(password)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])

    def test_authenticate_fails_with_wrong_password(self):
        password = self.faker.word()
        data = {"password": password}
        request = self.factory.post('authenticate', data)
        user =  mock.MagicMock(spec=AbstractBaseUser)
        user.check_password.return_value = False
        force_authenticate(request, user)
        response = self.controller.authenticate(request)
        user.check_password.assert_called_with(password)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])

    @mock.patch("AccountsApp.Controllers.auth_controller.Misc")
    @mock.patch("AccountsApp.Controllers.auth_controller.PasswordResetService")
    def test_send_password_reset_link(self, reset_service, misc):
        user_query = {"id": 1}
        misc.resolve_user_query.return_value = user_query
        request = self.factory.post('send-password-reset-link')
        request.META['HTTP_HOST'] = self.faker.url()
        response = self.controller.send_password_reset_link(request)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        reset_service.send_reset_link.assert_called_once()

    @mock.patch("AccountsApp.Controllers.auth_controller.Misc")
    @mock.patch("AccountsApp.Controllers.auth_controller.PasswordResetService")
    def test_send_password_reset_code(self, reset_service, misc):
        user_query = {"id": 1}
        misc.resolve_user_query.return_value = user_query
        signature = self.faker.sha1()
        reset_service.send_reset_code.return_value = signature
        request = self.factory.post('send-password-reset-code')
        response = self.controller.send_password_reset_code(request)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
        reset_service.send_reset_code.assert_called_once()

    @mock.patch("AccountsApp.Controllers.auth_controller.VerifierService")
    def test_reset_password_code_sets_password_if_valid(self, Verifier):
        data = {
            "code": str(self.faker.random_number),
            "signature": self.faker.sha1(),
            "new_password": self.faker.word()
        }
        request = self.factory.post('reset-password-code', data)
        user = mock.MagicMock(spec=AbstractBaseUser)
        Verifier.verify_password_reset.return_value = user
        response = self.controller.reset_password_code(request)
        Verifier.verify_password_reset.assert_called_with(
            data['code'], data['signature']
        )
        user.set_password.assert_called_once_with(data['new_password'])
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])


    @mock.patch("AccountsApp.Controllers.auth_controller.login")
    def test_change_password(self, login):
        data = {
            "new_password": self.faker.word(),
            "old_password": self.faker.word()
        }
        user = mock.MagicMock()
        user.check_password.return_value = False
        request = self.factory.post('change-password', data)
        force_authenticate(request, user)
        user.check_password.return_value = True
        response = self.controller.change_password(request)
        user.set_password.assert_called_once_with(data['new_password'])
        login.assert_called_once()
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])


    def test_change_password_fails_if_password_check_fails(self):
        data = {
            "new_password": self.faker.word(),
            "old_password": self.faker.word()
        }
        user = mock.MagicMock()
        user.check_password.return_value = False
        request = self.factory.post('change-password', data)
        force_authenticate(request, user)
        user.check_password.return_value = False
        response = self.controller.change_password(request)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['status'])