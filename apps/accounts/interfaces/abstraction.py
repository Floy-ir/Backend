from abc import ABC, abstractmethod
from . import dataclass


class AbstractAccountService(ABC):
    
    @abstractmethod
    def send_otp(self, request: dataclass.SendOTPRequest) -> bool:
        """Send OTP code to the specified mobile number."""
        pass
    
    @abstractmethod
    def verify_otp(self, request: dataclass.VerifyOTPRequest) -> bool:
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