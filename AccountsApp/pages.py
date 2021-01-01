from django.urls import path
from .Controllers import EmailVerificationController

def __verify_email(request):
    controller = EmailVerificationController.get_instance()
    return controller.verify_link(request)

urlpatterns = [
    path("verify-link/", __verify_email),
]  