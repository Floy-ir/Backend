import io
import uuid
import logging
from externals.s3 import interfaces as s3_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.accounts import interfaces as accounts_interfaces

from . import interfaces
from .models import UploadMetadata, FileMetadata

logger = logging.getLogger(__name__)

class FileStorageService(interfaces.AbstractFileStorageService):
    def __init__(
            self,
            claim: accounts_interfaces.Session,
            date_time_utils: date_time_interfaces.AbstractDateTime,
            s3_client_factory: s3_interfaces.AbstractS3ClientFactory,
            minio_bucket_name: str,
    ) -> None:
        self.claim = claim
        self.date_time_utils = date_time_utils
        self.s3_client_factory = s3_client_factory
        self.minio_bucket_name = minio_bucket_name
        self.minio_client = self.s3_client_factory.get_s3_client()

    def upload_files(
            self,
            caller: accounts_interfaces.Session,
            request: interfaces.UploadRequest
    ) -> interfaces.ImagesLink:
        logger.info(f'Caller: {caller}, Request UID: {request.uid}, Files: {[file.name for file in request.files]}')

        if caller.user.user_type != accounts_interfaces.UserType.INTERNAL:
            logger.warning(f"User {caller.user_uid} is not authorized to upload files.")
            raise interfaces.OnlyAdminException()

        try:
            upload_metadata, created = self._get_or_create_upload_metadata(request)
            self._delete_existing_files(upload_metadata, request)
            file_metadata_list, file_links = self._upload_files_to_minio(request, upload_metadata)

            FileMetadata.objects.bulk_create(file_metadata_list)
            if not created:
                upload_metadata.uploaded_at = self.date_time_utils.get_current_timestamp()
                upload_metadata.save()

        except Exception as e:
            logger.error(f'Error during file upload: {e}')
            raise interfaces.InternalFileStorageNotAvailable()

        return interfaces.ImagesLink(count=len(file_links), results=file_links)

    def _get_or_create_upload_metadata(self, request: interfaces.UploadRequest) -> (UploadMetadata, bool):
        upload_metadata, created = UploadMetadata.objects.get_or_create(
            uid=request.uid,
            defaults={
                'uploaded_at': self.date_time_utils.get_current_timestamp(),
                'uploaded_by': self.claim.user_uid
            }
        )
        return upload_metadata, created

    def _delete_existing_files(self, upload_metadata: UploadMetadata, request: interfaces.UploadRequest) -> None:
        existing_files = FileMetadata.objects.filter(upload_metadata=upload_metadata)
        for file in existing_files:
            logger.info(f"Removing file {file.file_name} from MinIO storage.")
            self.minio_client.remove_object(
                bucket_name=self.minio_bucket_name,
                object_name=f"{request.uid}/{file.file_name}"
            )
        existing_files.delete()

    def _upload_files_to_minio(self, request: interfaces.UploadRequest, upload_metadata: UploadMetadata) -> tuple:
        file_metadata_list = []
        file_links = []

        for file in request.files:
            self.minio_client.put_object(
                bucket_name=self.minio_bucket_name,
                object_name=f"{request.uid}/{file.name}",
                data=io.BytesIO(file.buffer),
                length=len(file.buffer),
            )

            presigned_url = self.minio_client.get_presigned_url(
                method='GET',
                bucket_name=self.minio_bucket_name,
                object_name=f"{request.uid}/{file.name}"
            )

            file_metadata_list.append(
                FileMetadata(
                    uid=str(uuid.uuid4()),
                    file_name=file.name,
                    file_size_in_bytes=len(file.buffer),
                    upload_metadata=upload_metadata,
                    file_link=presigned_url,
                )
            )
            file_links.append(presigned_url)

        return file_metadata_list, file_links

    def get_images_link(self, uid: str) -> interfaces.ImagesLink:
        try:
            upload_metadata = UploadMetadata.objects.get(uid=uid)
        except UploadMetadata.DoesNotExist:
            logger.warning(f"UploadMetadata with UID {uid} not found.")
            return interfaces.ImagesLink(count=0, results=[])

        try:
            file_links = [file.file_link for file in upload_metadata.files.all()]
        except Exception as e:
            logger.error(f'Error fetching file links: {e}')
            raise interfaces.InternalFileStorageNotAvailable()

        return interfaces.ImagesLink(count=len(file_links), results=file_links)
