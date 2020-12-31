import json
from AccountsApp.forms import SubmitEmailCode
from django.conf import settings
from AccountsApp import Services
from AccountsApp.utils.controller import Controller
from AccountsApp.utils.shortcuts import json_response
from rest_framework.decorators import api_view
from AccountsApp.Services.EmailVerificationService import EmailVerificationService
from AccountsApp.Services import VerifierService
from AccountsApp.Services import Misc
from rest_framework.request import Request

class EmailVerificationController(Controller):

    def __init__(self):
        self.base_url = settings.ACCOUNTS_APP['base_url']

    @Controller.route('send-verification-link')
    @Controller.decorate(api_view(['POST']))
    def send_verification_link(self, request: Request):
        user = Misc.resolve_user(request)
        service = EmailVerificationService(user, self.base_url)
        service.send_verification_link(request.META["HTTP_HOST"])
        return json_response(True)

    
    @Controller.route('send-verification-link')
    @Controller.decorate(api_view(['POST']))
    def send_verification_code(self, request):
        user = Misc.resolve_user(request)
        service = EmailVerificationService(user, self.base_url)
        service.send_verification_code()
        return json_response(True)
    
    @Controller.route('verify-code')
    @Controller.decorate(api_view(['POST']))
    def verify_code(self, request):
        form = SubmitEmailCode(request.data)
        self.validate_form(form)
        user_query = Misc.resolve_user_query(request)
        VerifierService.verify_email_code(user_query, request.data.get('code'))
        return json_response(True)
        
    
    @Controller.route('verify-link')
    @Controller.decorate(api_view(['POST']))
    def verify_link(self, request):
        pass