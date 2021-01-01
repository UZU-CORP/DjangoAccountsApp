from AccountsApp.constants import EMAIL_VERIF_URL
import json
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from AccountsApp.Services.EmailVerificationService import EmailVerificationService
from AccountsApp.Controllers import EmailVerificationController
from unittest import TestCase, mock
from rest_framework.decorators import api_view
from rest_framework.test import APIRequestFactory
from faker import Faker
from AccountsApp.utils.tests import TestMixin

class TestEmailVerificationController(TestCase, TestMixin):
    def setUp(self):
        self.faker = Faker()
        self.factory = APIRequestFactory()
        self.controller: EmailVerificationController = EmailVerificationController.get_instance()
        self.base_url: str = settings.ACCOUNTS_APP['base_url']
        self.http_host = 'hello.com'
        self.schemed_host = "https://{}".format(self.http_host)

    @mock.patch("AccountsApp.Controllers.email_verification_controller.EmailVerificationService")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.Misc")
    def test_send_verification_link(self, misc, service_class):
        user = mock.MagicMock(spec=AbstractBaseUser)
        misc.resolve_user.return_value = user
        service = mock.MagicMock(spec=EmailVerificationService)
        service_class.return_value = service
        request = self.factory.post('/send-verification-link/')
        request.META['HTTP_HOST'] = self.http_host
        response  = self.controller.send_verification_link(request)
        service.send_verification_link.assert_called_once_with(
            self.schemed_host, EMAIL_VERIF_URL
        )
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])
    
    @mock.patch("AccountsApp.Controllers.email_verification_controller.EmailVerificationService")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.Misc")
    def test_send_verification_code(self, misc, service_class):
        user = mock.MagicMock(spec=AbstractBaseUser)
        misc.resolve_user.return_value = user
        service = mock.MagicMock(spec=EmailVerificationService)
        service_class.return_value = service
        request = self.factory.post('send-verification-code/')
        response  = self.controller.send_verification_code(request)
        service.send_verification_code.assert_called_once_with()
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])

    @mock.patch("AccountsApp.Controllers.email_verification_controller.VerifierService")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.Misc")
    def test_verify(self, misc, verifier):
        user_query = {"id": 1}
        misc.resolve_user_query.return_value = user_query
        code = str( self.faker.random_number(4) )
        request = self.factory.post('verify-code/', {"code": code})
        response = self.controller.verify_code(request)
        verifier.verify_email_code.assert_called_once_with(user_query, code)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['status'])

    @mock.patch("AccountsApp.Controllers.email_verification_controller.settings.ACCOUNTS_APP")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.VerifierService")
    def test_verify_link_redirects_on_success(self, verifier, accounts):
        accounts_settings = {
            "sign_in_after_verification": False,
            "redirect_link": '/'
        }
        accounts.get.side_effect = accounts_settings.get
        user = mock.MagicMixin(spec=AbstractBaseUser)
        verifier.verify_email_link.return_value = user
        code_sig = self.faker.sha1()
        username_sig = self.faker.sha1()
        request = self.factory.get(
            'verify-link/', {"u": username_sig, "c": code_sig}
        )
        response = self.controller.verify_link(request)
        verifier.verify_email_link.assert_called_with(username_sig, code_sig)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, accounts_settings['redirect_link'])
    

    def test_verify_link_bad_request_on_bad_data(self):
        request = self.factory.get('verify-link/')
        response = self.controller.verify_link(request)
        self.assertEqual(response.status_code, 400)
    
    @mock.patch("AccountsApp.Controllers.email_verification_controller.login")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.settings.ACCOUNTS_APP")
    @mock.patch("AccountsApp.Controllers.email_verification_controller.VerifierService")
    def test_verify_link_login_on_success_if_set(self, verifier, accounts, login):
        accounts_settings = {
            "sign_in_after_verification": True,
            "redirect_link": '/'
        }
        accounts.get.side_effect = accounts_settings.get
        user = mock.MagicMixin(spec=AbstractBaseUser)
        verifier.verify_email_link.return_value = user
        code_sig = self.faker.sha1()
        username_sig = self.faker.sha1()
        request = self.factory.get(
            'verify-link/', {"u": username_sig, "c": code_sig}
        )
        self.controller.verify_link(request)
        login.assert_called_once()
