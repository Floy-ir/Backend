import logging
from . import interfaces

logger = logging.getLogger(__name__)


class MockSMSService(interfaces.AbstractSMSService):
    """
    Mock SMS service for development and testing.
    In production, this should be replaced with a real SMS provider like Twilio, Kavenegar, etc.
    """
    
    def send_sms(self, mobile: str, message: str) -> bool:
        """
        Mock implementation that logs the SMS instead of actually sending it.
        """
        logger.info(f"Mock SMS sent to {mobile}: {message}")
        print(f"[MOCK SMS] To: {mobile}, Message: {message}")
        return True
    
    def send_otp(self, mobile: str, code: str) -> bool:
        """
        Send OTP code via SMS.
        """
        message = f"Your verification code is: {code}"
        return self.send_sms(mobile, message)


class MockSMSServiceFactory(interfaces.AbstractSMSServiceFactory):
    """
    Factory for creating mock SMS service instances.
    """
    
    def get_sms_service(self) -> interfaces.AbstractSMSService:
        return MockSMSService()


# Example implementation for Kavenegar (Iranian SMS provider)
# Uncomment and configure when ready to use real SMS service
"""
import requests
from typing import Optional

class KavenegarSMSService(interfaces.AbstractSMSService):
    def __init__(self, api_key: str, sender: str = "10008663"):
        self.api_key = api_key
        self.sender = sender
        self.base_url = "https://api.kavenegar.com/v1"
    
    def send_sms(self, mobile: str, message: str) -> bool:
        try:
            url = f"{self.base_url}/{self.api_key}/sms/send.json"
            data = {
                "receptor": mobile,
                "sender": self.sender,
                "message": message
            }
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send SMS via Kavenegar: {e}")
            return False
    
    def send_otp(self, mobile: str, code: str) -> bool:
        message = f"کد تایید شما: {code}"
        return self.send_sms(mobile, message)

class KavenegarSMSServiceFactory(interfaces.AbstractSMSServiceFactory):
    def __init__(self, api_key: str, sender: str = "10008663"):
        self.api_key = api_key
        self.sender = sender
    
    def get_sms_service(self) -> interfaces.AbstractSMSService:
        return KavenegarSMSService(self.api_key, self.sender)
"""
