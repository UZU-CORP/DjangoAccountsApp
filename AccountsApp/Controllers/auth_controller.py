from AccountsApp.constants import PASSWORD_RESET_URL
from AccountsApp.Models.two_factor import TwoFactorTokens
from AccountsApp.utils.decorators import ensure_signed_in
from AccountsApp.signals import SignedUp
from django.contrib.auth import authenticate, login, logout

from AccountsApp.forms import PasswordChangeForm, PasswordResetCodeForm, TwoFactorTokenForm
from django.conf import settings
from AccountsApp import Services
from AccountsApp.utils.controller import Controller
from AccountsApp.utils.shortcuts import json_response
from rest_framework.decorators import api_view
from AccountsApp.Services import PasswordResetService, TwoFactorService, VerifierService
from AccountsApp.Services import Misc
from rest_framework.request import Request
from django.db import IntegrityError
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger("AccountsApp.AuthController")
class AuthController(Controller):

    def get_signup_form(self):
        form_path = settings.ACCOUNTS_APP.get("signup_form", None)
        if form_path:
            return self.__class__._get_func_from_path(form_path)

    @Controller.route('sign-up')
    @Controller.decorate(api_view(['POST']))
    def signup(self, request):
        form = self.get_signup_form()
        payload = None
        if form:
            self.validate_form(form)
            payload = form.cleaned_data
        try:
            payload = payload or request.data.dict().copy()
            keep_signed_in = payload.pop("keep_signed_in", "false")
            password = payload.pop("password")
            user = User(**payload)
            user.set_password(password)
            user.save()
            if keep_signed_in == "false":
                request.session.set_expiry(0)
            login(request, user)
            SignedUp.send('signedup', request=request, user=user)
        except IntegrityError as e:
            logger.error(e)
            return json_response(False, error="Signup error")
        except Exception as e:
            logger.error(e)
            return json_response(False, error="Signup error")
        else:
            return json_response(True)

    @Controller.route('sign-in')
    @Controller.decorate(api_view(['POST']))
    def signin(self, request: Request):
        """
        logs the user in
        """
        credentials = {
            User.USERNAME_FIELD: request.data.get(User.USERNAME_FIELD, None), 
            "password": request.data.get("password")
        }
        user = authenticate(**credentials)
        if not user:
            return json_response(False, error="Incorrect credentials")
        if not request.data.get("keep_signed_in", "false") == "false":
            request.session.set_expiry(0)
        if ( hasattr(user, "two_factor_enabled") 
            and getattr(user, "two_factor_enabled") ):
            signature = TwoFactorService.send_token(user)
            duration = settings.ACCOUNTS_APP["2fa_duration"]
            return json_response(
                True, 
                data={"signature": signature, "expiry": duration}
            )
        login(request, user)
        return json_response(True)

    @Controller.route('authenticate')
    @Controller.decorate(api_view(['POST']), ensure_signed_in)
    def authenticate(self, request: Request):
        if request.user.check_password(request.data.get("password")):
            return json_response(True)
        else:
            return json_response(False)

    @Controller.route('send-password-reset-link')
    @Controller.decorate(api_view(['POST']))
    def send_password_reset_link(self, request: Request):
        user =  Misc.resolve_user(request)
        PasswordResetService.send_reset_link(
            user,
            "https://" + request.META['HTTP_HOST'],
            settings.ACCOUNTS_APP["base_url"],
            PASSWORD_RESET_URL
        )
        return json_response(True)

    @Controller.route('send-password-reset-code')
    @Controller.decorate(api_view(['POST']))
    def send_password_reset_code(self, request: Request):
        user =  Misc.resolve_user(request)
        signature = PasswordResetService.send_reset_code(user)
        return json_response(True, {"signature": signature})
    
    @Controller.route('reset-password')
    @Controller.decorate(api_view(['POST']))
    def reset_password_code(self, request):
        """
            Replaced username with signature
        """
        form = PasswordResetCodeForm(request.data)
        self.validate_form(form)
        data = form.cleaned_data
        code = data.get("code")
        signature = data.get("signature")
        password = data.get("new_password")
        user = VerifierService.verify_password_reset(code, signature)
        user.set_password(password)
        user.save()
        return json_response(True)


    @Controller.route("reset-password-link")
    @Controller.decorate(api_view(['POST']))
    def reset_password_link(self, request: Request):
        response = json_response(False)
        response.status_code = 500
    
    @Controller.route('change-password')
    @Controller.decorate(api_view(['POST']), ensure_signed_in)
    def change_password(self, request):
        form = PasswordChangeForm(request.data)
        self.validate_form(form)
        data = form.cleaned_data
        if request.user.check_password(data["old_password"]):
            request.user.set_password(data["new_password"])
            login(request, request.user)
            return json_response(True)
        return json_response(False, error="Invalid password")


    @Controller.route('sign-out')
    @Controller.decorate(api_view(['POST']))
    def signout(self, request):
        try:
            logout(request)
        except:
            pass
        return json_response(True)
    
    @Controller.route('verify-2fa')
    @Controller.decorate(api_view(['POST']))
    def verify_2fa(self, request):
        form = TwoFactorTokenForm(request.data)
        self.validate_form(form)
        data = form.cleaned_data
        data['provider']  =  data.get('provider', TwoFactorTokens.EMAIL)
        user = VerifierService.verify_2fa_token(**data)
        login(request, user)
        return json_response(True)