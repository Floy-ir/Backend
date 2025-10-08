from libs import exceptions


class Forbbiden(exceptions.ForbiddenRoot):
    pass


class BadRequest(exceptions.BadRequestRoot):
    pass


class NotFound(exceptions.NotFoundRoot):
    pass


class UsedUidException(BadRequest):
    def __init__(self):
        super().__init__('uid has been used before.')


class UsedPhoneNumberException(BadRequest):
    def __init__(self):
        super().__init__('mobile number has been used before.')


class UsedUsernameException(BadRequest):
    def __init__(self):
        super().__init__('username has been used before.')


class UserNotFound(NotFound):
    def __init__(self):
        super().__init__('user not exist')

class SessionNotFound(NotFound):
    def __init__(self):
        super().__init__('no session found corresponding to this session_uid')


class InvalidTokenException(BadRequest):
    def __init__(self):
        super().__init__('the authentication token is invalid')


class SessionTimeout(BadRequest):
    def __init__(self):
        super().__init__('too much time has passed from last activity')


class TerminatedSessionException(BadRequest):
    def __init__(self):
        super().__init__('already logged out')


class WrongPasswordException(BadRequest):
    def __init__(self):
        super().__init__('wrong password entered')


class InvalidOTPException(BadRequest):
    def __init__(self):
        super().__init__('invalid or expired OTP code')


class OTPExpiredException(BadRequest):
    def __init__(self):
        super().__init__('OTP code has expired')


class OTPAlreadyUsedException(BadRequest):
    def __init__(self):
        super().__init__('OTP code has already been used')
