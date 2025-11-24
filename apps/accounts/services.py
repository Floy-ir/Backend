from uuid import uuid4
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from . import interfaces
from utils.date_time import interfaces as date_time_interfaces
from utils.http_requester import interfaces as http_requester_interfaces
from .models import EitaUser, User, OTP
from externals.sms.services import MockSMSServiceFactory
from externals.sms import interfaces as sms_interfaces
import logging
import os

logger = logging.getLogger(__name__)


class AccountService(interfaces.AbstractAccountService):
    def __init__(self,
                 date_time: date_time_interfaces.AbstractDateTime,
                 claim: interfaces.Session = None,
                 session_life_time_in_second: int = 24 * 60 * 60,
                 sms_service_factory: sms_interfaces.AbstractSMSServiceFactory = None,
                 http_requester: http_requester_interfaces.AbstractHTTPRequester = None,
                 ):
        self.claim = claim
        self.session_life_time_in_second = session_life_time_in_second
        if sms_service_factory is None:
            sms_service_factory = MockSMSServiceFactory()
        self.sms_service = sms_service_factory.get_sms_service()
        self.date_time_utils = date_time
        self.http_requester = http_requester 
    
    def send_otp(self, request: interfaces.SendOTPRequest) -> interfaces.SendOTPResponse:
        """
        Send OTP code to the specified mobile number.
        """
        # Generate OTP code and UUID
        code = OTP.generate_code()
        otp_uuid = str(uuid4())
        logger.info(f"Generated OTP code: {code} and UUID: {otp_uuid} for mobile: {request.mobile}")
        
        # Get current timestamp
        current_time = int(timezone.now().timestamp())
        expires_at = current_time + (5 * 60)  # 5 minutes from now
        
        # Invalidate any existing OTP for this mobile
        OTP.objects.filter(mobile=request.mobile, is_used=False).update(is_used=True)
        
        # Create new OTP record
        otp = OTP.objects.create(
            mobile=request.mobile,
            code=code,
            uuid=otp_uuid,
            created_at=current_time,
            expires_at=expires_at
        )
        
        logger.info(f"Created OTP record for {request.mobile}, calling SMS service...")
        
        # Send SMS
        success = self.sms_service.send_otp(request.mobile, code)
        
        logger.info(f"SMS service returned: {success}")
        
        if success:
            logger.info(f"OTP sent successfully to {request.mobile}")
            return interfaces.SendOTPResponse(success=True, otp_uuid=otp_uuid)
        else:
            # If SMS failed, mark OTP as used so it can't be verified
            otp.is_used = True
            otp.save()
            logger.error(f"Failed to send OTP to {request.mobile}")
            raise interfaces.SMSServiceFailedException()
    
    def verify_otp(self, request: interfaces.VerifyOTPRequest) -> interfaces.VerifyOTPResponse:
        """
        Verify OTP code for the specified mobile number.
        """
        current_time = int(timezone.now().timestamp())
        
        # Find valid OTP by UUID, mobile, and code
        otp = OTP.objects.filter(
            uuid=request.otp_uuid,
            mobile=request.mobile,
            code=request.code,
            is_used=False,
            expires_at__gt=current_time
        ).first()
        
        if not otp:
            logger.warning(f"Invalid or expired OTP for {request.mobile} with UUID {request.otp_uuid}")
            raise interfaces.InvalidOTPException()
        
        # Mark OTP as verified and used
        otp.is_verified = True
        otp.is_used = True
        otp.save()
        
        logger.info(f"OTP verified successfully for {request.mobile} with UUID {request.otp_uuid}")
        return interfaces.VerifyOTPResponse(success=True, otp_uuid=request.otp_uuid)
    
    def signup(self, request: interfaces.SignupRequest) -> interfaces.AuthResponse:
        """
        Complete user signup after OTP verification.
        """
        # First check if OTP was verified successfully
        current_time = int(timezone.now().timestamp())
        verified_otp = OTP.objects.filter(
            uuid=request.otp_uuid,
            mobile=request.mobile,
            is_verified=True,
            expires_at__gt=current_time
        ).first()
        
        if not verified_otp:
            logger.warning(f"No verified OTP found for {request.mobile} with UUID {request.otp_uuid}")
            raise interfaces.OTPVerificationRequiredException()
        
        # Check if user already exists
        if User.objects.filter(mobile=request.mobile).exists():
            raise interfaces.UsedPhoneNumberException()
        
        # Create new user
        user = User.objects.create_user(
            username=request.mobile,  # Use mobile as username
            mobile=request.mobile,
            password=request.password,
            full_name=request.full_name,
            uid=str(uuid4())
        )
        
        # Set timestamps
        current_time = int(timezone.now().timestamp())
        user.created_at = current_time
        user.modified_at = current_time
        user.save()
        
        # Create session token (simplified - in production use JWT or similar)
        token = str(uuid4())
        
        # Create user dataclass for response
        user_data = interfaces.User(
            uid=user.uid,
            username=user.username,
            mobile=user.mobile,
            full_name=user.full_name,
            user_type=interfaces.UserType.ORDINARY,
            created_at=user.created_at,
            modified_at=user.modified_at
        )
        
        logger.info(f"User signed up successfully: {request.mobile}")
        return interfaces.AuthResponse(token=token, user=user_data)
    
    def login(self, request: interfaces.LoginRequest) -> interfaces.AuthResponse:
        """
        Authenticate user with mobile and password.
        """
        # Find user by mobile
        try:
            user = User.objects.get(mobile=request.mobile)
        except User.DoesNotExist:
            raise interfaces.UserNotFound()
        
        # Authenticate user
        authenticated_user = authenticate(
            username=user.username,
            password=request.password
        )
        
        if not authenticated_user:
            raise interfaces.WrongPasswordException()
        
        # Create session token
        token = str(uuid4())
        
        # Update last login timestamp
        current_time = int(timezone.now().timestamp())
        user.modified_at = current_time
        user.save()
        
        # Create user dataclass for response
        user_data = interfaces.User(
            uid=user.uid,
            username=user.username,
            mobile=user.mobile,
            full_name=user.full_name,
            user_type=interfaces.UserType.ORDINARY,
            created_at=user.created_at,
            modified_at=user.modified_at
        )
        
        logger.info(f"User logged in successfully: {request.mobile}")
        return interfaces.AuthResponse(token=token, user=user_data)
    
    def forgot_password(self, request: interfaces.ForgotPasswordRequest) -> interfaces.ForgotPasswordResponse:
        """
        Send OTP for password reset to the specified mobile number.
        """
        # Check if user exists
        try:
            user = User.objects.get(mobile=request.mobile)
        except User.DoesNotExist:
            logger.warning(f"User not found for mobile: {request.mobile}")
            raise interfaces.UserNotFound()
        
        # Generate OTP code and UUID
        code = OTP.generate_code()
        otp_uuid = str(uuid4())
        logger.info(f"Generated OTP code: {code} and UUID: {otp_uuid} for password reset mobile: {request.mobile}")
        
        # Get current timestamp
        current_time = int(timezone.now().timestamp())
        expires_at = current_time + (5 * 60)  # 5 minutes from now
        
        # Invalidate any existing OTP for this mobile
        OTP.objects.filter(mobile=request.mobile, is_used=False).update(is_used=True)
        
        # Create new OTP record
        otp = OTP.objects.create(
            mobile=request.mobile,
            code=code,
            uuid=otp_uuid,
            created_at=current_time,
            expires_at=expires_at
        )
        
        logger.info(f"Created OTP record for password reset {request.mobile}, calling SMS service...")
        
        # Send SMS
        success = self.sms_service.send_otp(request.mobile, code)
        
        logger.info(f"SMS service returned: {success}")
        
        if success:
            logger.info(f"Password reset OTP sent successfully to {request.mobile}")
            return interfaces.ForgotPasswordResponse(
                success=True,
                otp_uuid=otp_uuid
            )
        else:
            # If SMS failed, mark OTP as used so it can't be verified
            otp.is_used = True
            otp.save()
            logger.error(f"Failed to send password reset OTP to {request.mobile}")
            raise interfaces.SMSServiceFailedException()
    
    def reset_password(self, request: interfaces.ResetPasswordRequest) -> interfaces.ForgotPasswordResponse:
        """
        Reset user password after OTP verification.
        """
        # First check if OTP was verified successfully
        current_time = int(timezone.now().timestamp())
        verified_otp = OTP.objects.filter(
            uuid=request.otp_uuid,
            mobile=request.mobile,
            is_verified=True,
            expires_at__gt=current_time
        ).first()
        
        if not verified_otp:
            logger.warning(f"No verified OTP found for password reset {request.mobile} with UUID {request.otp_uuid}")
            raise interfaces.OTPVerificationRequiredException()
        
        # Find user
        try:
            user = User.objects.get(mobile=request.mobile)
        except User.DoesNotExist:
            logger.warning(f"User not found for password reset mobile: {request.mobile}")
            raise interfaces.UserNotFound()
        
        # Update user password
        user.set_password(request.new_password)
        user.modified_at = current_time
        user.save()
        
        logger.info(f"Password reset successfully for user: {request.mobile}")
        return interfaces.ForgotPasswordResponse(
            success=True,
        )


    def eita_login(self, request: interfaces.EitaLoginRequest) -> interfaces.EitaLoginResponse:
        """
        Login user with Eita ID and password.
        """
        # Find user by Eita ID
        current_time = self.date_time_utils.get_current_timestamp()

        try:
            user = EitaUser.objects.get(eita_id=request.eita_id)
            user.last_login_at = current_time
            user.save()
        except EitaUser.DoesNotExist:
            user = EitaUser.objects.create(
                uid=str(uuid4()),
                eita_id=request.eita_id,
                created_at=current_time,
                last_login_at=current_time
            )

        if request.mobile != None: 
            user.mobile = request.mobile 
            user.save()

        return interfaces.EitaLoginResponse(success=True)

    def send_eita_message(self, request: interfaces.SendEitaMessageRequest) -> interfaces.SendEitaMessageResponse:
        """
        Send message to Eita users who haven't received initial message.
        """
        if request.message_type != interfaces.EitaTypeMessage.INITIAL:
            logger.warning(f"Unsupported message type: {request.message_type}")
            raise interfaces.UnsupportedMessageTypeException()
        
        # Get Eita token from environment
        eita_token = os.getenv('EITA_TOKEN', '5768337691:AAGDAe6rjxu1cUgxK4BizYi--Utc3J9v5AU')
        
        # Default message text if not provided
        message_text = request.text or "سلام \n  این یک پیام تست است"
        
        # Get all users who haven't received initial message
        users = EitaUser.objects.filter(initial_message_sent=False)
        
        sent_count = 0
        failed_count = 0
        
        if not self.http_requester:
            logger.error("HTTP requester is not configured")
            raise interfaces.HTTPRequesterNotConfiguredException()
        
        for user in users:
            try:
                # Convert eita_id to integer (chat_id)
                try:
                    chat_id = int(user.eita_id)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid eita_id for user {user.uid}: {user.eita_id}")
                    failed_count += 1
                    continue
                
                # Prepare request payload
                payload = {
                    "token": eita_token,
                    "chat_id": chat_id,
                    "text": message_text
                }
                
                # Send HTTP POST request to Eita API
                response = self.http_requester.post(
                    url="https://eitaayar.ir/api/app/sendMessage",
                    json=payload,
                    parse_response_as_json=True,
                    timeout=(10, 30)
                )
                
                # Check if request was successful
                if response.status_code == 200 and response.content_json:
                    result = response.content_json
                    if result.get("ok") == True and result.get("result") == "success":
                        # Mark message as sent
                        user.initial_message_sent = True
                        user.save()
                        sent_count += 1
                        logger.info(f"Successfully sent message to Eita user {user.uid} (chat_id: {chat_id})")
                    else:
                        logger.warning(f"Failed to send message to Eita user {user.uid} (chat_id: {chat_id}): {result}")
                        failed_count += 1
                else:
                    logger.warning(f"HTTP request failed for Eita user {user.uid} (chat_id: {chat_id}): status_code={response.status_code}")
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending message to Eita user {user.uid}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Eita message sending completed. Sent: {sent_count}, Failed: {failed_count}")
        return interfaces.SendEitaMessageResponse(
            success=True,
            sent_count=sent_count,
            failed_count=failed_count
        )
