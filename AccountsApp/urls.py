from django.urls import path
from . import Controllers


urlpatterns = [
    path("", Controllers.EmailVerificationController()),
    path("", Controllers.AuthController())
]  