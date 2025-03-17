import abc


class AbstractS3Client(abc.ABC):
    """
    Amazon S3, minio or our s3 implementations all must implement this interface.
    In fact this interface is reverse engineered based on minio sdk.
    Methods that probably we need, should be written here.
    """

    @abc.abstractmethod
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
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    def get_presigned_url(
            self,
            method: str,
            bucket_name: str,
            object_name: str
    ) -> str:
        raise NotImplementedError

    def remove_object(
            self,
            bucket_name: str,
            object_name: str,
            version_id: str | None = None
    ):
        raise NotImplementedError


class AbstractS3ClientFactory(abc.ABC):
    def get_s3_client(self) -> AbstractS3Client:
        raise NotImplementedError
