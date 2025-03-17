from django.contrib import admin
from .models import UploadMetadata, FileMetadata

@admin.register(UploadMetadata)
class UploadMetadataAdmin(admin.ModelAdmin):
    list_display = ('uid','uploaded_at')

@admin.register(FileMetadata)
class FileMetadataAdmin(admin.ModelAdmin):
    list_display = ('uid','file_name')