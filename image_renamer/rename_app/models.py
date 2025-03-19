from django.db import models
import uuid

# Create your models here.

class FileUpload(models.Model):
    Title = models.CharField(max_length=100)
    uKey = models.UUIDField(default=uuid.uuid4,unique=True,editable=False, null=True, blank=True)
    fullURL = models.CharField(max_length=1000, blank=True, null=True)
    imageNameDict = models.TextField(blank=True, null=True)
    renamedZipFileURL = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.Title