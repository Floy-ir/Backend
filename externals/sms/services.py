import json
import logging
import sys
import requests
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
        print(f"\n{'='*50}")
        print(f"[MOCK SMS] To: {mobile}")
        print(f"[MOCK SMS] Message: {message}")
        print(f"{'='*50}\n")
        return True
    
    def send_otp(self, mobile: str, code: str) -> bool:
        """
        Send OTP code via SMS.
        """
        message = f"کد تایید فلوی: {code}"
        
        # Log to logger
        logger.info(f"Mock OTP sent to {mobile}: {code}")
        
        # Print to console with forced flush
        print(f"\n{'='*60}", flush=True)
        print(f"🔐 OTP CODE FOR {mobile}", flush=True)
        print(f"📱 Code: {code}", flush=True)
        print(f"⏰ Valid for 5 minutes", flush=True)
        print(f"{'='*60}\n", flush=True)
        
        # Also write to stderr to ensure it shows up
        print(f"OTP CODE: {code} for {mobile}", file=sys.stderr, flush=True)
        
        return self.send_sms(mobile, message)


class MockSMSServiceFactory(interfaces.AbstractSMSServiceFactory):
    """
    Factory for creating mock SMS service instances.
    """
    
    def get_sms_service(self) -> interfaces.AbstractSMSService:
        return MockSMSService()


class MelipayamakSMSService(interfaces.AbstractSMSService):
    """
    Melipayamak SMS service implementation.
    """
    
    def __init__(self, api_key: str, sender: str):
        self.api_key = api_key
        self.sender = sender
        self.base_url = "https://console.melipayamak.com/api/send/simple"
    
    def send_sms(self, mobile: str, message: str) -> bool:
        """
        Send SMS message via Melipayamak API.
        """
        try:
            url = f"{self.base_url}/{self.api_key}"
            payload = json.dumps({
                "from": self.sender,
                "to": mobile,
                "text": message
            })
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, data=payload)
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {mobile} via Melipayamak")
                return True
            else:
                logger.error(f"Failed to send SMS via Melipayamak. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send SMS via Melipayamak: {e}")
            return False
    
    def send_otp(self, mobile: str, code: str) -> bool:
        """
        Send OTP code via SMS.
        """
        message = f"کد تایید فلوی: {code}"
        return self.send_sms(mobile, message)


class MelipayamakSMSServiceFactory(interfaces.AbstractSMSServiceFactory):
    """
    Factory for creating Melipayamak SMS service instances.
    """
    
    def __init__(self, api_key: str, sender: str):
        self.api_key = api_key
        self.sender = sender
    
    def get_sms_service(self) -> interfaces.AbstractSMSService:
        return MelipayamakSMSService(self.api_key, self.sender)

