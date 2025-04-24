from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import FileUpload
import os
from .utils import *
import pandas as pd


def upload(request):
    uploaded_files_name = []
    all_files_in_folder = []
    context = {}
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        is_valid = validate_image_extensions(files)
        print("files",files)
        print("is_valid",is_valid)
        status = is_valid.get('status')
        if status == 'success':
            user_name = "User_name"
            upload_obj = FileUpload(Title=user_name)
            upload_obj.save()
            formatted_date = upload_obj.created_at.strftime('%Y%m%d')
            foldername = f"{formatted_date}_{str(upload_obj.uKey)}"
            media_root = settings.MEDIA_ROOT
            create_folder(media_root, foldername)
            folder_path = foldername
            upload_obj.fullURL = folder_path
            upload_obj.save()
            Full_folder_path = os.path.join(media_root, foldername)
            fs = FileSystemStorage(location=Full_folder_path)
            for file in files:
                fs.save(file.name, file)
            return redirect(f"rename/{upload_obj.id}")
        else:
            context={
               'success_message': is_valid, 
            }
    return render(request, 'index.html', context)
    
   


def rename_files(request, pk):
    fileobj = get_object_or_404(FileUpload, id=pk)
    folder_path = fileobj.fullURL
    media_root = settings.MEDIA_ROOT
    Full_folder_path = os.path.join(media_root, folder_path)
    uploaded_files_name = get_files_in_folder(Full_folder_path, allow_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'])
    uploaded_files_name_clean={}
    
    uploaded_files_name_clean = clean_images_name(uploaded_files_name)
    print("uploaded_files_name_clean",uploaded_files_name_clean)
    base_url = request.build_absolute_uri('/')
    excelFilePath = create_excel_file(uploaded_files_name_clean, Full_folder_path, base_url)
    print("excelFilePath",excelFilePath)
    
    
    if request.method == 'POST':
        if 'file-rename-submit' in request.POST:
            files = request.FILES.get('renameList')
            rename_list_file_foldername = 'rename_list_file'
            create_folder(Full_folder_path, rename_list_file_foldername)

            if files:
                rename_list_file_path = os.path.join(Full_folder_path, rename_list_file_foldername, files.name)

                # Replace the old file if it already exists
                if os.path.exists(rename_list_file_path):
                    os.remove(rename_list_file_path)

                # Save the new uploaded file
                with open(rename_list_file_path, 'wb+') as destination:
                    for chunk in files.chunks():
                        destination.write(chunk)

                # Now you can read from the saved file
                uploaded_files_name_clean = excel_to_dict(rename_list_file_path)
                request.session['uploaded_files_name_clean'] = uploaded_files_name_clean

                print("uploaded_files_name_clean", uploaded_files_name_clean)
    
        if 'rename-submit' in request.POST:
            rename_dict = {}
            for key, value in request.POST.items():
                print("key: ",key)
                if key != 'csrfmiddlewaretoken' and key != 'rename-submit':
                    rename_dict[key] = value         

            rename_message = rename_file_names(Full_folder_path, rename_dict, allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'])
            print("rename_message:",rename_message)
            renamed_files_path = os.path.join(Full_folder_path, 'renamed_files')
            renamedZipFileURL = zip_folder(renamed_files_path, 'renamed_files.zip')
            renamedZipFileURLShort = f"{folder_path}\\renamed_files\\renamed_files.zip"
            fileobj.renamedZipFileURL = renamedZipFileURLShort
            fileobj.save()
            request.session['rename_dict'] = rename_dict
            request.session['rename_message'] = rename_message
            
            return redirect(reverse('download_zip', args=[pk]))
    
    # Use the uploaded_files_name_clean from session if available
    if 'uploaded_files_name_clean' in request.session:
        uploaded_files_name_clean = request.session['uploaded_files_name_clean']
        request.session.flush()

    context = {
        'uploaded_files_name': uploaded_files_name_clean,
        'ImageNameFileURL' : excelFilePath,
    }
    
    return render(request, 'rename.html', context)


def download_zip(request, pk):
    context={}
    fileobj = get_object_or_404(FileUpload, id=pk)
    rename_dict = request.session.get('rename_dict', {})
    success_message = request.session.get('rename_message', {})
    renamedZipFileURL = fileobj.renamedZipFileURL
    media_root = settings.MEDIA_ROOT
    Full_renamedZipFileURL = os.path.join(media_root, renamedZipFileURL)
    print("renamedZipFileURL inside download view: ",Full_renamedZipFileURL)
    context = {
        'rename_dict':rename_dict,
        'fileobj': fileobj,
        'success_message': success_message,
    }
    return render(request, 'download.html', context)


def download_file(request, pk):
    fileobj = get_object_or_404(FileUpload, id=pk)
    zip_file_path = fileobj.renamedZipFileURL
    media_root = settings.MEDIA_ROOT
    Full_zip_file_path = os.path.join(media_root, zip_file_path)
    request.session.flush()
    # print("zip_file_path inside download_file view:", Full_zip_file_path)

    if not os.path.exists(Full_zip_file_path):
        raise Http404("Zip file not found")

    try:
        response = FileResponse(open(Full_zip_file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(Full_zip_file_path)}'
        return response
    except Exception as e:
        print(f"Error opening file: {e}")
        raise Http404("Error occurred while downloading the file")
    

# # This is the delete_folder view
# def delete_folder(request, pk):
#     print("Delete view")
#     try:
#         # Get the file object by its primary key (ID)
#         fileobj = FileUpload.objects.get(id=pk)
        
#         # Get the folder path where files are stored (this assumes the folder path is saved in the model)
#         folder_path = fileobj.folder_path
        
#         # Check if the folder exists and delete it
#         if os.path.exists(folder_path):
#             shutil.rmtree(folder_path)
#             print(f"Deleted folder: {folder_path}")
#         else:
#             print(f"Folder does not exist: {folder_path}")

#         return HttpResponse("Folder deleted successfully.", status=200)

#     except UploadedFile.DoesNotExist:
#         return HttpResponse("File not found.", status=404)
#     except Exception as e:
#         return HttpResponse(f"Error deleting folder: {str(e)}", status=500)
