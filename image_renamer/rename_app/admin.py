from django.contrib import admin
from .models import FileUpload

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ('Title', 'uKey', 'fullURL', 'renamedZipFileURL', 'created_at', 'updated_at')
    search_fields = ('Title', 'fullURL')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('uKey', 'created_at', 'updated_at')

admin.site.register(FileUpload, FileUploadAdmin)
