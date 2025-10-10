import abc


class AbstractSMSService(abc.ABC):
    """
    SMS service interface for sending OTP and other SMS messages.
    Different SMS providers (Twilio, Kavenegar, etc.) should implement this interface.
    """

    @abc.abstractmethod
    def send_sms(self, mobile: str, message: str) -> bool:
        """
        Send SMS message to the specified mobile number.
        
        Args:
            mobile: The mobile number to send SMS to
            message: The message content to send
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        raise NotImplementedError

    @abc.abstractmethod
    def send_otp(self, mobile: str, code: str) -> bool:
        """
        Send OTP code to the specified mobile number.
        
        Args:
            mobile: The mobile number to send OTP to
            code: The OTP code to send
            
        Returns:
            bool: True if OTP was sent successfully, False otherwise
        """
        raise NotImplementedError


class AbstractSMSServiceFactory(abc.ABC):
    def get_sms_service(self) -> AbstractSMSService:
        raise NotImplementedError
