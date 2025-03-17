from externals.s3 import interfaces as s3_interfaces
from utils.date_time.interfaces import AbstractDateTime


class FakeS3Client(s3_interfaces.AbstractS3Client):
    def __init__(self, available=True):
        self.available = available
        self.uploaded_files = []

    def put_object(
            self,
            bucket_name: str,
            object_name: str,
            data,
            length: int,
            content_type: str = "application/octet-stream",
            metadata: dict = None,
            sse=None,
            progress=None,
            part_size: int = 0,
            num_parallel_uploads=3,
            tags=None,
            retention=None,
            legal_hold: bool = False,
    ):
        if not self.available:
            raise Exception("S3 is not available")
        self.uploaded_files.append({
            'bucket_name': bucket_name,
            'object_name': object_name,
            'data': data,
            'length': length,
            'content_type': content_type,
            'metadata': metadata
        })

    def get_object(
            self,
            bucket_name: str,
            object_name: str,
            offset: int = 0,
            length: int = 0,
            request_headers: dict[str, str] | None = None,
            ssec=None,
            version_id: str | None = None,
            extra_query_params: dict[str, str] | None = None
    ):
        if not self.available:
            raise Exception("S3 is not available")
        
        # Return a fake response object that matches what the real S3 client would return
        class FakeResponse:
            def read(self):
                return b'fake_content'
            
            def close(self):
                pass
            
            def release_conn(self):
                pass
        
        return FakeResponse()

    def remove_object(
            self,
            bucket_name: str,
            object_name: str,
            version_id: str | None = None
    ):
        self.uploaded_files = []

    def get_presigned_url(
            self,
            method: str,
            bucket_name: str,
            object_name: str
    ) -> str:
        if not self.available:
            raise Exception("S3 is not available")
        return f"https://fake-s3.example.com/{bucket_name}/{object_name}"

    def upload_file(self, file_path: str, bucket_name: str, object_name: str) -> None:
        if not self.available:
            raise Exception("S3 is not available")
        self.uploaded_files.append({
            'file_path': file_path,
            'bucket_name': bucket_name,
            'object_name': object_name
        })


class FakeS3ClientFactory(s3_interfaces.AbstractS3ClientFactory):
    def __init__(self, available=True, hostname="fake-s3.example.com", access_key="fake-key", secret_key="fake-secret"):
        self.available = available
        self.hostname = hostname
        self.access_key = access_key
        self.secret_key = secret_key

    def get_s3_client(self) -> s3_interfaces.AbstractS3Client:
        return FakeS3Client(available=self.available)


class ConstantDateTimeUtils(AbstractDateTime):
    def __init__(self, constant: int):
        self.constant = constant

    def get_current_timestamp(self) -> int:
        return self.constant

    def get_start_timestamp_of_day_from_today(self, timedelta_days: int) -> int:
        pass

    def get_end_timestamp_of_day_from_today(self, timedelta_days: int) -> int:
        pass

    def get_start_timestamp_of_day(self, timestamp: int) -> int:
        pass

    def get_end_timestamp_of_day(self, timestamp: int) -> int:
        pass
