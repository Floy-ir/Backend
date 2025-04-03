from libs import exceptions as lib_exceptions


class BadRequest(lib_exceptions.BadRequestRoot):
    pass


class Forbidden(lib_exceptions.ForbiddenRoot):
    pass


class NotFound(lib_exceptions.NotFoundRoot):
    pass

class ServiceUnavailable(lib_exceptions.ServiceUnavailableRoot):
    pass


class WebsiteNotFound(NotFound):
    def __init__(self):
        super().__init__("website doesn't exist")


class FileStorageNotAvailable(ServiceUnavailable):
    def __init__(self):
        super().__init__("file storage is not available")


class UnsupportedRequestType(BadRequest):
    def __init__(self):
        super().__init__("unsupported request type")


class UnsuccessfulRequest(BadRequest):
    def __init__(self):
        super().__init__("unsuccessful request")
