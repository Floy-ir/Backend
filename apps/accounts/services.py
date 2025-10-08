from uuid import uuid4
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from . import interfaces
from utils.date_time import interfaces as date_time_interfaces
from .models import User, OTP
from externals.sms.services import MockSMSServiceFactory
import logging

logger = logging.getLogger(__name__)


class AccountService(interfaces.AbstractAccountService):
    def __init__(self,
                 claim: interfaces.Session = None,
                 session_life_time_in_second: int = 24 * 60 * 60
                 ):
        self.claim = claim
        self.session_life_time_in_second = session_life_time_in_second
        self.sms_service = MockSMSServiceFactory().get_sms_service()
    
    def send_otp(self, request: interfaces.SendOTPRequest) -> bool:
        """
        Send OTP code to the specified mobile number.
        """
        try:
            # Generate OTP code
            code = OTP.generate_code()
            logger.info(f"Generated OTP code: {code} for mobile: {request.mobile}")
            
            # Get current timestamp
            current_time = int(timezone.now().timestamp())
            expires_at = current_time + (5 * 60)  # 5 minutes from now
            
            # Invalidate any existing OTP for this mobile
            OTP.objects.filter(mobile=request.mobile, is_used=False).update(is_used=True)
            
            # Create new OTP record
            otp = OTP.objects.create(
                mobile=request.mobile,
                code=code,
                created_at=current_time,
                expires_at=expires_at
            )
            
            logger.info(f"Created OTP record for {request.mobile}, calling SMS service...")
            
            # Send SMS
            success = self.sms_service.send_otp(request.mobile, code)
            
            logger.info(f"SMS service returned: {success}")
            
            if success:
                logger.info(f"OTP sent successfully to {request.mobile}")
                return True
            else:
                # If SMS failed, mark OTP as used so it can't be verified
                otp.is_used = True
                otp.save()
                logger.error(f"Failed to send OTP to {request.mobile}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending OTP to {request.mobile}: {e}")
            return False
    
    def verify_otp(self, request: interfaces.VerifyOTPRequest) -> bool:
        """
        Verify OTP code for the specified mobile number.
        """
        try:
            current_time = int(timezone.now().timestamp())
            
            # Find valid OTP
            otp = OTP.objects.filter(
                mobile=request.mobile,
                code=request.code,
                is_used=False,
                expires_at__gt=current_time
            ).first()
            
            if not otp:
                logger.warning(f"Invalid or expired OTP for {request.mobile}")
                return False
            
            # Mark OTP as used
            otp.is_used = True
            otp.save()
            
            logger.info(f"OTP verified successfully for {request.mobile}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying OTP for {request.mobile}: {e}")
            return False
    
    def signup(self, request: interfaces.SignupRequest) -> interfaces.AuthResponse:
        """
        Complete user signup after OTP verification.
        """
        try:
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
            
        except interfaces.UsedPhoneNumberException:
            raise
        except Exception as e:
            logger.error(f"Error during signup for {request.mobile}: {e}")
            raise interfaces.BadRequest("Signup failed")
    
    def login(self, request: interfaces.LoginRequest) -> interfaces.AuthResponse:
        """
        Authenticate user with mobile and password.
        """
        try:
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
            
        except (interfaces.UserNotFound, interfaces.WrongPasswordException):
            raise
        except Exception as e:
            logger.error(f"Error during login for {request.mobile}: {e}")
            raise interfaces.BadRequest("Login failed")
