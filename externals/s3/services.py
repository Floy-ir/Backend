from minio import Minio
import json

from . import interfaces

class MinioClientFactory(interfaces.AbstractS3ClientFactory):
    def __init__(self, hostname: str, access_key: str, secret_key: str, bucket_name: str, secure: bool = False, public_url: str = None):
        self.hostname = hostname
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.secure = secure
        self.public_url = public_url or hostname

    def get_s3_client(self) -> interfaces.AbstractS3Client:
        print(f"Initializing Minio client for hostname: {self.hostname}")

        client = Minio(
            self.hostname,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        # Always set the bucket policy, even if bucket exists
        try:
            if not client.bucket_exists(self.bucket_name):
                client.make_bucket(self.bucket_name)
                print(f"Bucket '{self.bucket_name}' created successfully.")
            
            # Set bucket policy to public read
            policy = json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                    }
                ]
            })
            client.set_bucket_policy(self.bucket_name, policy)
            print(f"Bucket policy set for '{self.bucket_name}'.")
            
            # Verify the policy was set
            current_policy = client.get_bucket_policy(self.bucket_name)
            print(f"Current bucket policy: {current_policy}")
            
        except Exception as e:
            print(f"Error setting bucket policy: {e}")
            raise

        # Override the get_presigned_url method to use public_url
        original_get_presigned_url = client.get_presigned_url
        def get_presigned_url(*args, **kwargs):
            # Instead of using presigned URL, return the public URL
            object_name = kwargs.get('object_name', args[2] if len(args) > 2 else None)
            if object_name:
                url = f"{self.public_url}/{self.bucket_name}/{object_name}"
                print(f"Generated public URL: {url}")
                return url
            return original_get_presigned_url(*args, **kwargs)
        client.get_presigned_url = get_presigned_url

        return client
