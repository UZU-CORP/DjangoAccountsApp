from AccountsApp.utils.decorators import ensure_signed_in
from AccountsApp.signals import SignedUp
from django.contrib.auth import authenticate, login

from AccountsApp.forms import PasswordChangeForm, PasswordResetCodeForm
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

    @Controller.route('signup')
    @Controller.decorate(api_view(['POST']))
    def signup(self, request):
        form = self.get_signup_form()
        if form:
            self.validate_form(form)
        try:
            payload = request.data.dict().copy()
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

    @Controller.route('signout')
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
        user_query =  Misc.resolve_user_query(request)
        PasswordResetService.send_reset_link(
            user_query,
            request.META['HTTP_HOST'],
            settings.ACCOUNTS_APP["base_url"],
            "verify-link/"
        )
        return json_response(True)

    @Controller.route('send-password-reset-coode')
    @Controller.decorate(api_view(['POST']))
    def send_password_reset_code(self, request: Request):
        user_query =  Misc.resolve_user_query(request)
        signature = PasswordResetService.send_reset_code(user_query)
        return json_response(True, {"signature": signature})
    
    @Controller.route('reset-password-code')
    @Controller.decorate(api_view(['POST']))
    def reset_password_code(self, request):
        form = PasswordResetCodeForm(request.data)
        self.validate_form(form)
        data = form.cleaned_data
        code = data.get("code")
        signature = data.get("signature")
        password = data.get("new_password")
        user = VerifierService.verify_password_reset(code, signature)
        user.set_password(password)
        return json_response(True)


    @Controller.route('reset-password-link')
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


