# rename_app/urls.py
from django.urls import path
from .views import  upload, rename_files,download_zip,download_file

urlpatterns = [
    path('', upload, name='upload'),
    path('rename/<int:pk>/', rename_files, name='rename_files'),
    path('download/<int:pk>/', download_zip, name='download_zip'),
    path('download_file/<int:pk>/', download_file, name='download_file'),
    # path('delete_folder/<int:pk>/', delete_folder, name='delete_folder'),

]
