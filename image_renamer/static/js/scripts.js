document.addEventListener('DOMContentLoaded', (event) => {
    const fileInput = document.querySelector('#file-input');
    console.log('fileInput:', fileInput);
    const uploadMessage = document.querySelector('.upload-message');
    const loader = document.querySelector('#loader');
    const select_files_btn = document.querySelector('#select-files-btn');

    // select_files_btn.addEventListener('click',showLoader);
    fileInput.addEventListener('change', handleFileSelection);  // Handle file selection and update file count

    function showLoader() {
        setTimeout(() => {  
            loader.style.display = 'block';
            }, 5000);
    }

    function handleFileSelection() {
        // Perform any necessary processing of the selected files here
        // Hide the loader once processing is complete
        if (fileInput.files.length > 0) {
            uploadMessage.textContent = `${fileInput.files.length} file(s) selected`;
        } else {
            uploadMessage.textContent = 'Click the button to upload or drag files to the page';
        }
        loader.style.display = 'none';  // Hide the loader after processing
    }





    
});
