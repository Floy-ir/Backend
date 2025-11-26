from abc import ABC, abstractmethod
from . import dataclass


class AbstractAccountService(ABC):
    
    @abstractmethod
    def send_otp(self, request: dataclass.SendOTPRequest) -> dataclass.SendOTPResponse:
        """Send OTP code to the specified mobile number."""
        pass
    
    @abstractmethod
    def verify_otp(self, request: dataclass.VerifyOTPRequest) -> dataclass.VerifyOTPResponse:
        """Verify OTP code for the specified mobile number."""
        pass
    
    @abstractmethod
    def signup(self, request: dataclass.SignupRequest) -> dataclass.AuthResponse:
        """Complete user signup after OTP verification."""
        pass
    
    @abstractmethod
    def login(self, request: dataclass.LoginRequest) -> dataclass.AuthResponse:
        """Authenticate user with mobile and password."""
        pass
    
    @abstractmethod
    def forgot_password(self, request: dataclass.ForgotPasswordRequest) -> dataclass.ForgotPasswordResponse:
        """Send OTP for password reset to the specified mobile number."""
        pass
    
    @abstractmethod
    def reset_password(self, request: dataclass.ResetPasswordRequest) -> dataclass.ForgotPasswordResponse:
        """Reset user password after OTP verification."""
        pass
    
    @abstractmethod
    def send_eita_message(self, request: dataclass.SendEitaMessageRequest) -> dataclass.SendEitaMessageResponse:
        """Send message to Eita users who haven't received initial message."""
        pass
    
    @abstractmethod
    def send_bale_message(self, request: dataclass.SendBaleMessageRequest) -> dataclass.SendBaleMessageResponse:
        """Send message to Bale users who haven't received initial message."""
        pass
    
    @abstractmethod
    def send_telegram_message(self, request: dataclass.SendTelegramMessageRequest) -> dataclass.SendTelegramMessageResponse:
        """Send message to Telegram users who haven't received initial message."""
        pass