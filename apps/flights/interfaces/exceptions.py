from libs import exceptions as lib_exceptions


class BadRequest(lib_exceptions.BadRequestRoot):
    pass


class Forbidden(lib_exceptions.ForbiddenRoot):
    pass


class NotFound(lib_exceptions.NotFoundRoot):
    pass
