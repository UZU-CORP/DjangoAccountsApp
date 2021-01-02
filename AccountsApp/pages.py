from AccountsApp.constants import EMAIL_VERIF_URL
from django.urls import path
from .Controllers import EmailVerificationController

def __verify_email(request):
    controller = EmailVerificationController.get_instance()
    return controller.verify_link(request)

urlpatterns = [
    path(EMAIL_VERIF_URL, __verify_email),
]  