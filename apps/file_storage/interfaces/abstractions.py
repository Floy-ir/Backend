import abc
from apps.accounts import interfaces as accounts_interfaces
from .dataclasses import UploadMetadata, UploadRequest, UploadMetadataFilter, UploadMetadataResult, ImagesLink


class AbstractFileStorageService(abc.ABC):
    def upload_files(self, caller: accounts_interfaces.Session,
                     upload_request: UploadRequest) -> UploadMetadata:
        """ This method should not be exposed as a HTTP endpoint. only other apps can call it.
        It validates files based on their names, sizes, count, etc. if OK, it saves them in its internal storage.

        Args:
            caller (Session): the caller. for now, it can be only apps
            upload_request (UploadRequest): including files

        Returns:
            UploadMetadata: contains metadata about the file upload

        Raises:
            OnlyAdminException
            UsedUidException
            InvalidUUIDException
            InternalFileStorageNotAvailable
        """
        raise NotImplementedError


    def get_images_link(self, uid: str) -> ImagesLink:
        """
        by this method, you can find url of files in minIO.
        just internal app can call this method. 
        this method doesn't exposed to user.

        Args:
            uid: str

        Returns:
            ImagesLink
        """

