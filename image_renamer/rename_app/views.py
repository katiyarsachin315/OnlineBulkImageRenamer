from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import FileUpload
import os
from .utils import validate_image_extensions,create_folder,get_files_in_folder,rename_file_names,zip_folder,clean_images_name,rename_list_upload_file,rename_files_with_given_list
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
            # files = request.FILES.getlist('files')
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
    uploaded_files_name = get_files_in_folder(Full_folder_path)
    uploaded_files_name_clean={}
    
    uploaded_files_name_clean = clean_images_name(uploaded_files_name)
    
    if request.method == 'POST':
        if 'file-rename-submit' in request.POST:
            files = request.FILES.get('renameList')
            rename_list_file_foldername = 'rename_list_file'
            create_folder(Full_folder_path, rename_list_file_foldername)
            print("files",files)
            rename_list_file_path = f"{Full_folder_path}\\{rename_list_file_foldername}"
            print("rename_list_file_path",rename_list_file_path)
            if (files):
                images_name_array = rename_list_upload_file(files, rename_list_file_path)
                uploaded_files_name_clean = rename_files_with_given_list(images_name_array, uploaded_files_name_clean)
                
                request.session['uploaded_files_name_clean'] = uploaded_files_name_clean
    
        if 'rename-submit' in request.POST:
            rename_dict = {}
            for key, value in request.POST.items():
                print("key: ",key)
                if key != 'csrfmiddlewaretoken' and key != 'rename-submit':
                    rename_dict[key] = value         

            rename_message = rename_file_names(Full_folder_path, rename_dict)
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