import logging
from user_agents import parse
from rest_framework import authentication, permissions
from runner.bootstrap import get_bootstrapper
from libs import exceptions as lib_exceptions
from apps.accounts import interfaces as accounts_interfaces

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = "Bearer"
    ip = ''

    def authenticate(self, request):
        self.ip = get_client_ip(request)
        parsed_user_agent = parse(request.META.get('HTTP_USER_AGENT'))
        self.user_agent = str(parsed_user_agent)
        self.is_public_view = not bool(request.parser_context["view"].get_permissions()) or \
                              isinstance(request.parser_context["view"].get_permissions()[0], permissions.AllowAny)

        token = request.META.get('HTTP_AUTHORIZATION')
        if not self.is_public_view and not token:
            raise lib_exceptions.NotAuthenticated("Authentication credentials were not provided.")
        logger.debug(f'request ip = {self.ip}')

        key = None if not token or len(token.split()) != 2 else token.split()[1]
        return self.authenticate_credentials(key)

    def authenticate_credentials(self, key):
        accounts_service = get_bootstrapper().get_account_service()
        access_metadata = accounts_interfaces.AccessMetadata(
            ip=self.ip,
            user_agent=self.user_agent
        )
        if self.is_public_view:
            return None, access_metadata
        try:
            user_session = accounts_service.authenticate(
                request=accounts_interfaces.AuthenticateRequest(
                    token=key,
                    access_metadata=access_metadata
                )
            )
            return user_session, access_metadata
        except accounts_interfaces.BadRequest as e:
            raise lib_exceptions.NotAuthenticated(e)
