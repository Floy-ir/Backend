from minio import Minio

from . import interfaces

class MinioClientFactory(interfaces.AbstractS3ClientFactory):
    def __init__(self, hostname: str, access_key: str, secret_key: str, bucket_name: str):
        self.hostname = hostname
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name

    def get_s3_client(self) -> interfaces.AbstractS3Client:
        print(f"Initializing Minio client for hostname: {self.hostname}")

        client = Minio(
            self.hostname,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False # TODO: need to inject from bootstrap
        )

        if not client.bucket_exists(self.bucket_name):
            client.make_bucket(self.bucket_name)
            print(f"Bucket '{self.bucket_name}' created successfully.")
        else:
            print(f"Bucket '{self.bucket_name}' already exists.")

        return client
