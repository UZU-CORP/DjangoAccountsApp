import json
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Services.EmailVerificationService import EmailVerificationService
from django.http import response
from AccountsApp.Controllers.EmailVerificationController import EmailVerificationController
from unittest import TestCase, mock
from rest_framework.decorators import api_view
from rest_framework.test import APIRequestFactory
from faker import Faker
from AccountsApp.utils.tests import TestMixin

class TestEmailVerificationController(TestCase, TestMixin):
    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.controller = EmailVerificationController.get_instance()
        self.base_url: str = settings.ACCOUNTS_APP['base_url']
        self.http_host = self.faker.url()

    @mock.patch("AccountsApp.Controllers.EmailVerificationController.EmailVerificationService")
    @mock.patch("AccountsApp.Controllers.EmailVerificationController.Misc")
    def test_send_verification_link(self, misc, service_class):
        user = mock.MagicMock(spec=AbstractBaseUser)
        misc.resolve_user.return_value = user
        service = mock.MagicMock(spec=EmailVerificationService)
        service_class.return_value = service
        request = self.factory.post('/send-verification-link/')
        request.META['HTTP_HOST'] = self.http_host
        response  = self.controller.send_verification_link(request)
        service.send_verification_link.assert_called_once_with(self.http_host)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
    
    @mock.patch("AccountsApp.Controllers.EmailVerificationController.EmailVerificationService")
    @mock.patch("AccountsApp.Controllers.EmailVerificationController.Misc")
    def test_send_verification_code(self, misc, service_class):
        user = mock.MagicMock(spec=AbstractBaseUser)
        misc.resolve_user.return_value = user
        service = mock.MagicMock(spec=EmailVerificationService)
        service_class.return_value = service
        request = self.factory.post('/send-verification-code/')
        response  = self.controller.send_verification_code(request)
        service.send_verification_code.assert_called_once_with()
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])

        
