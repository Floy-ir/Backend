class ServiceExceptions(Exception):
    pass


class BadRequestRoot(ServiceExceptions):
    status_code = 400


class ForbiddenRoot(ServiceExceptions):
    status_code = 403


class NotFoundRoot(ServiceExceptions):
    status_code = 404


class ServiceUnavailableRoot(ServiceExceptions):
    status_code = 424


class NotAuthenticated(ServiceExceptions):
    status_code = 401


class TooManyRequestRoot(ServiceExceptions):
    status_code = 429