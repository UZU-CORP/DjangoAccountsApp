from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from htmailer import Htmessage

accounts_settings = settings.ACCOUNTS_APP
headers = None
site_name = "Our platform"
try:
    site_name = getattr(settings, "APP_NAME", None)  or settings.SITE_NAME
    if settings.EMAIL_FROM and  settings.EMAIL_HOST_USER:
        headers={
            'From': '{} <{}>'.format(
                settings.EMAIL_FROM, settings.EMAIL_HOST_USER
            )
        }
except AttributeError:
    pass

def mail_user(user, message, subject='', connection=None):
    email_address = [user.email]
    template, context = message
    context['site_name'] = site_name
    msg = Htmessage(
        subject=subject, 
        to=email_address,
        headers = headers
    ).txt_template(template, context)
    if connection:
        msg.connection = connection
    msg.send() 
    
def send_email_verification_link(user, url: str):
    template = accounts_settings.get(
        "email_verification_link_template",
        "AccountsApp/default_email_verification_link.html"
    )
    context = {
        "url": url,
        "name": user.first_name
    }
    message = (template, context)
    subject = "Email verification"
    mail_user(user, message, subject)

def send_email_verification_code(user, code: str):
    template = accounts_settings.get(
        "email_verification_code_template",
        "AccountsApp/default_email_verification_code.html"
    )
    context = {
        "code": code,
        "name": user.first_name
    }
    message = (template, context)
    subject = "Email verification"
    mail_user(user, message, subject)

def send_password_reset_code(user, code: str):
    template = accounts_settings.get(
        "email_verification_code_template",
        "AccountsApp/default_password_reset_code.html"
    )
    context = {
        "code": code,
        "name": user.first_name
    }
    message = (template, context)
    subject = "Password reset code"
    mail_user(user, message, subject)

def send_password_reset_link(user, url: str):
    template = accounts_settings.get(
        "email_verification_code_template",
        "AccountsApp/default_password_reset_link.html"
    )
    context = {
        "url": url,
        "name": user.first_name
    }
    message = (template, context)
    subject = "Password Reset"
    mail_user(user, message, subject)

def send_two_factor_token(user, code: str ):
    template = accounts_settings.get(
        "email_verification_code_template",
        "AccountsApp/default_two_factor_code.html"
    )
    context = {
        "code": code,
        "name": user.first_name
    }
    message = (template, context)
    subject = "Two factor authentication"
    mail_user(user, message, subject)