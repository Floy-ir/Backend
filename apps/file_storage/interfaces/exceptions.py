from libs import exceptions as lib_exceptions


class Forbidden(lib_exceptions.ForbiddenRoot):
    pass


class OnlyAdminException(Forbidden):
    def __init__(self):
        super().__init__('Only admin users can do this.')


class OnlyAdminOrUploaderException(Forbidden):
    def __init__(self):
        super().__init__('Only admin users or the user that the file is uploaded on his behalf can do this.')


class BadRequest(lib_exceptions.BadRequestRoot):
    pass


class UsedUidException(BadRequest):
    def __init__(self):
        super().__init__('uid has been used before.')


class InvalidUUIDException(BadRequest):
    def __init__(self):
        super().__init__('uid is not a valid UUID')


class NotFound(lib_exceptions.NotFoundRoot):
    pass


class UploadMetadataNotFound(NotFound):
    def __init__(self):
        super().__init__('The requested uploaded files not found')


class ServiceUnavailable(lib_exceptions.ServiceUnavailableRoot):
    pass


class InternalFileStorageNotAvailable(ServiceUnavailable):
    def __init__(self):
        super().__init__('The internal file storage service is not available now. please try again later.')
