from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from runner.bootstrap import get_bootstrapper
from . import interfaces
import logging

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.GenericViewSet):
    """
    ViewSet for handling account-related operations including signup and login.
    """

    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        """
        Send OTP code to the specified mobile number.
        """
        try:
            service = get_bootstrapper().get_account_service()
            
            # Validate request data
            send_otp_request = interfaces.SendOTPRequest(**request.data)
            
            # Send OTP
            success = service.send_otp(send_otp_request)
            
            if success:
                return response.Response({
                    'success': True,
                    'message': 'OTP sent successfully'
                }, status=status.HTTP_200_OK)
            else:
                return response.Response({
                    'success': False,
                    'message': 'Failed to send OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in send_otp view: {e}")
            return response.Response({
                'success': False,
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        """
        Verify OTP code for the specified mobile number.
        """
        try:
            service = get_bootstrapper().get_account_service()
            
            # Validate request data
            verify_otp_request = interfaces.VerifyOTPRequest(**request.data)
            
            # Verify OTP
            is_valid = service.verify_otp(verify_otp_request)
            
            if is_valid:
                return response.Response({
                    'success': True,
                    'message': 'OTP verified successfully'
                }, status=status.HTTP_200_OK)
            else:
                return response.Response({
                    'success': False,
                    'message': 'Invalid or expired OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in verify_otp view: {e}")
            return response.Response({
                'success': False,
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        """
        Complete user signup after OTP verification.
        """
        try:
            service = get_bootstrapper().get_account_service()
            
            # Validate request data
            signup_request = interfaces.SignupRequest(**request.data)
            
            # Complete signup
            auth_response = service.signup(signup_request)
            
            return response.Response({
                'success': True,
                'message': 'User signed up successfully',
                'data': auth_response.model_dump()
            }, status=status.HTTP_201_CREATED)
            
        except interfaces.UsedPhoneNumberException as e:
            return response.Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in signup view: {e}")
            return response.Response({
                'success': False,
                'message': 'Signup failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
        Authenticate user with mobile and password.
        """
        try:
            service = get_bootstrapper().get_account_service()
            
            # Validate request data
            login_request = interfaces.LoginRequest(**request.data)
            
            # Authenticate user
            auth_response = service.login(login_request)
            
            return response.Response({
                'success': True,
                'message': 'User logged in successfully',
                'data': auth_response.model_dump()
            }, status=status.HTTP_200_OK)
            
        except interfaces.UserNotFound as e:
            return response.Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except interfaces.WrongPasswordException as e:
            return response.Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in login view: {e}")
            return response.Response({
                'success': False,
                'message': 'Login failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
