from rest_framework import viewsets, response, permissions
from runner.bootstrap import get_bootstrapper
from . import interfaces
import logging

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    def send_otp(self, request):
        service = get_bootstrapper().get_account_service()
        send_otp_request = interfaces.SendOTPRequest(**request.data)
        results = service.send_otp(send_otp_request)
        return response.Response(results.model_dump())

    def verify_otp(self, request):
        service = get_bootstrapper().get_account_service()
        verify_otp_request = interfaces.VerifyOTPRequest(**request.data)
        results = service.verify_otp(verify_otp_request)
        return response.Response(results.model_dump())

    def signup(self, request):
        service = get_bootstrapper().get_account_service()
        signup_request = interfaces.SignupRequest(**request.data)
        results = service.signup(signup_request)
        return response.Response(results.model_dump())

    def login(self, request):
        service = get_bootstrapper().get_account_service()
        login_request = interfaces.LoginRequest(**request.data)
        results = service.login(login_request)
        return response.Response(results.model_dump())

    def forgot_password(self, request):
        service = get_bootstrapper().get_account_service()
        forgot_password_request = interfaces.ForgotPasswordRequest(**request.data)
        results = service.forgot_password(forgot_password_request)
        return response.Response(results.model_dump())

    def reset_password(self, request):
        service = get_bootstrapper().get_account_service()
        reset_password_request = interfaces.ResetPasswordRequest(**request.data)
        results = service.reset_password(reset_password_request)
        return response.Response(results.model_dump())

    def eita_login(self, request):
        service = get_bootstrapper().get_account_service()
        eita_login_request = interfaces.EitaLoginRequest(**request.data)
        results = service.eita_login(eita_login_request)
        return response.Response(results.model_dump())

    def send_eita_message(self, request):
        service = get_bootstrapper().get_account_service()
        send_message_request = interfaces.SendEitaMessageRequest(**request.data)
        results = service.send_eita_message(send_message_request)
        return response.Response(results.model_dump())

    def bale_login(self, request):
        service = get_bootstrapper().get_account_service()
        bale_login_request = interfaces.BaleLoginRequest(**request.data)
        results = service.bale_login(bale_login_request)
        return response.Response(results.model_dump())

    def send_bale_message(self, request):
        service = get_bootstrapper().get_account_service()
        send_message_request = interfaces.SendBaleMessageRequest(**request.data)
        results = service.send_bale_message(send_message_request)
        return response.Response(results.model_dump())