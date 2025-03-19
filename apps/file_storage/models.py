from django.db import models


class UploadMetadata(models.Model):
    uid = models.CharField(max_length=128, unique=True, primary_key=True)
    uploaded_at = models.PositiveBigIntegerField(null=True)
    uploaded_by = models.CharField(max_length=128, null=True)


class FileMetadata(models.Model):
    uid = models.CharField(max_length=128, unique=True, primary_key=True)
    upload_metadata = models.ForeignKey(UploadMetadata, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=100)
    file_link = models.CharField(max_length=2048, null=True)
    file_size_in_bytes = models.IntegerField()
