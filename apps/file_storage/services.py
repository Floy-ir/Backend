import io
import uuid
from django.db import transaction

from externals.s3 import interfaces as s3_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.accounts import interfaces as accounts_interfaces

from . import interfaces
from .models import UploadMetadata, FileMetadata

# TODO: find a policy to crawl image from website

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
    ) -> interfaces.UploadMetadata:
        print(f'caller: {caller}, request: {request.uid}, files: {[file.name for file in request.files]}')
        if caller.user.user_type != accounts_interfaces.UserType.INTERNAL:
            print(f"user {caller} is not admin.")
            raise interfaces.OnlyAdminException()

        try:
            upload_metadata, created = UploadMetadata.objects.get_or_create(
                uid=request.uid,
                defaults={
                    'uploaded_at': self.date_time_utils.get_current_timestamp(),
                    'uploaded_by': caller.user_uid
                }
            )

            # Delete all existing files for the uid in the bucket
            existing_files = FileMetadata.objects.filter(upload_metadata=upload_metadata)
            for file in existing_files:
                self.minio_client.remove_object(
                    bucket_name=self.minio_bucket_name,
                    object_name=f"{request.uid}/{file.file_name}"
                )
            existing_files.delete()

            file_metadata_list = []
            for file in request.files:
                self.minio_client.put_object(
                    bucket_name=self.minio_bucket_name,
                    object_name=f"{request.uid}/{file.name}",
                    data=io.BytesIO(file.buffer),
                    length=len(file.buffer),
                )
                file_metadata_list.append(
                    FileMetadata(
                        uid=str(uuid.uuid4()),
                        file_name=file.name,
                        file_size_in_bytes=len(file.buffer),
                        upload_metadata=upload_metadata
                    )
                )

            FileMetadata.objects.bulk_create(file_metadata_list)

            if not created:
                upload_metadata.uploaded_at = self.date_time_utils.get_current_timestamp()
                upload_metadata.save()

        except Exception as e:
            print(f'internal file storage unavailable: {e}')
            raise interfaces.InternalFileStorageNotAvailable()

        result = self._convert_upload_metadata_to_dataclass(upload_metadata)
        print(f'final result: {result}')
        return result


    def get_images_link(self, uid: str) -> interfaces.ImagesLink:
        try:
            upload_metadata = UploadMetadata.objects.get(uid=uid)
        except UploadMetadata.DoesNotExist:
            return interfaces.ImagesLink(
                count=0,
                results=[]
            )

        try:
            files = upload_metadata.files.all()
            links = [
                self.minio_client.get_presigned_url(
                    method='GET',
                    bucket_name=self.minio_bucket_name,
                    object_name=f'{uid}/{file.file_name}'
                ) for file in files
            ]
        except Exception as e:
            print(f'internal file storage unavailable: {e}')
            raise interfaces.InternalFileStorageNotAvailable()

        return interfaces.ImagesLink(
            count=len(links),
            results=links
        )

    def _convert_upload_metadata_to_dataclass(self, upload_metadata: UploadMetadata) -> interfaces.UploadMetadata:
        return interfaces.UploadMetadata(
            uid=upload_metadata.uid,
            uploaded_at=upload_metadata.uploaded_at,
            uploaded_by=upload_metadata.uploaded_by,
            files=[self._convert_file_metadata_to_dataclass(file) for file in upload_metadata.files.all()]
        )

    @staticmethod
    def _convert_file_metadata_to_dataclass(file_metadata: FileMetadata) -> interfaces.FileMetadata:
        return interfaces.FileMetadata(
            file_name=file_metadata.file_name,
            file_size_in_bytes=file_metadata.file_size_in_bytes,
        )
