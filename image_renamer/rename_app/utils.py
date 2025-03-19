from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
import shutil
import zipfile
import os
from django.http import HttpResponse
import re
import pandas as pd


def validate_image_extensions(uploaded_files):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
    error_files = []

    for uploaded_file in uploaded_files:
        file_extension = os.path.splitext(uploaded_file.name)[1][1:].lower()

        if file_extension not in valid_extensions:
            print(f"Unsupported file extension '{file_extension}' in file '{uploaded_file.name}'.")
            error_files.append(uploaded_file.name)

    if error_files:
        return {
            "status": "error",
            "message": f"Unsupported file extension. Errors occurred for files: {', '.join(error_files)}"
        }

    return {"status": "success", "message": "All files are valid."}

def create_folder(path, folder_name):
    full_path = os.path.join(path, folder_name)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        print(f"Folder '{folder_name}' created at '{path}'.")
    else:
        print(f"Folder '{folder_name}' already exists at '{path}'.")



def get_files_in_folder(folder_path):
    if not os.path.exists(folder_path):
        return {}
    
    files_dict = {}
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            files_dict[filename] = filename
            
    return files_dict

def rename_file_names(src_path, rename_dict):
    try:
        # Ensure the provided path exists and is a directory
        if not os.path.exists(src_path):
            raise ValueError(f"The path {src_path} does not exist.")
        if not os.path.isdir(src_path):
            raise ValueError(f"The path {src_path} is not a directory.")

        # Create the 'renamed_files' folder inside the source path if it doesn't exist
        renamed_files_path = os.path.join(src_path, 'renamed_files')
        if not os.path.exists(renamed_files_path):
            os.makedirs(renamed_files_path)
            print(f"Created directory: {renamed_files_path}")

        # Clear all files in the directory if any
        dst_path = f"{src_path}\\renamed_files"
        [os.remove(os.path.join(dst_path, f)) for f in os.listdir(dst_path) if os.path.isfile(os.path.join(dst_path, f))]

        # List all files in the directory
        files = [f for f in os.listdir(src_path) if os.path.isfile(os.path.join(src_path, f))]

        # Rename files based on the provided dictionary
        success_files = []
        error_files = []

        for file in files:
            if file in rename_dict:
                new_file_name = rename_dict[file]
                old_file_path = os.path.join(src_path, file)
                new_file_path = os.path.join(renamed_files_path, new_file_name)
                shutil.copy(old_file_path, new_file_path)
                print(f"Renamed and copied: {file} to {new_file_name} in {renamed_files_path}")
                success_files.append(file)
            else:
                print(f"No rename entry found for: {file}")
                error_files.append(file)
        
        if len(success_files) == len(files):
            return {
                "status": "success",
                "message": "All images renamed successfully! Please click on download button to download the renamed images."
            }
        else:
            return {
                "status": "error",
                "message": f"Some files were not renamed. Errors occurred for files: {', '.join(error_files)}"
            }

    except Exception as e:
        print(f"An error occurred: {e}")
        
def zip_folder(folder_path, zip_name):
    zip_path = os.path.join(folder_path, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip the zip file itself
                if file_path == zip_path:
                    continue
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    
    return zip_path

def clean_images_name(uploaded_files_name):
        uploaded_files_name_clean={}
        text_to_replace = '_'
        for key, value in uploaded_files_name.items():
            cleaned_name = re.sub(r'[^a-zA-Z0-9.]', text_to_replace, re.sub(r'[\[\]\(\)\{\}]', '', value))
            cleaned_name = re.sub(r'_+', '_', cleaned_name)
            uploaded_files_name_clean[key] = cleaned_name
        return uploaded_files_name_clean

def rename_list_upload_file(files, rename_list_file_path):
   # Remove existing files in the directory
   [os.remove(os.path.join(rename_list_file_path, f)) 
    for f in os.listdir(rename_list_file_path) 
    if os.path.isfile(os.path.join(rename_list_file_path, f))]

   # Save the uploaded file to the specified location
   fs = FileSystemStorage(location=rename_list_file_path)
   fs.save(files.name, files)

   # Read the Excel file into a DataFrame
   rename_list_df = pd.read_excel(files, sheet_name=0, header=None)

   # Flatten the DataFrame and convert to a list of strings
   images_name_list = rename_list_df.values.flatten().astype(str)
           
   # Convert the numpy array to a list
   images_name_array = images_name_list.tolist()

   return images_name_array


def rename_files_with_given_list(images_name_array, uploaded_files_name_clean):
    matchedImageName = []

    # Iterate over the image names
    for img_name in images_name_array:
        img_name_val = img_name.split('.')[0]  # Extract the name without the extension
        
        # Iterate over the keys in the uploaded_files_name_clean dictionary
        for key, key_name in uploaded_files_name_clean.items():
            key_name = str(key_name).split('.')[0]  # Extract the key name without the extension
            
            if img_name_val in key_name:  # If the image name is found in the key name
                matchedImageName.append(img_name_val)
                increment_variable = images_name_array.index(img_name) + 1
                file_extension = 'png'
                
                print("matchedImageName:", matchedImageName)
                print("increment_variable:", increment_variable)
                print("file_extension:", file_extension)
                print("key_name matched:", key_name)
                
                imgCount = matchedImageName.count(img_name_val)
                print("imgCount:", imgCount)
                
                # Update the dictionary based on the count of occurrences
                if imgCount > 1:
                    uploaded_files_name_clean[key] = f"{increment_variable}_{imgCount-1}_{img_name_val}.{file_extension}"
                else:
                    uploaded_files_name_clean[key] = f"{increment_variable}_{img_name_val}.{file_extension}"

    return uploaded_files_name_clean

