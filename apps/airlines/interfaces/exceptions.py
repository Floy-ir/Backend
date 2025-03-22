from libs import exceptions as lib_exceptions


class BadRequest(lib_exceptions.BadRequestRoot):
    pass


class Forbidden(lib_exceptions.ForbiddenRoot):
    pass


class NotFound(lib_exceptions.NotFoundRoot):
    pass

class ServiceUnavailable(lib_exceptions.ServiceUnavailableRoot):
    pass

class AirlineNotFound(NotFound):
    def __init__(self):
        super().__init__("airline doesn't exist")




class FileStorageNotAvailable(ServiceUnavailable):
    def __init__(self):
        super().__init__("file storage is not available")
