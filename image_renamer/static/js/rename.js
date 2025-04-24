document.addEventListener('DOMContentLoaded', () => {
    const toggleCheckbox = document.getElementById('toggle-checkbox');
    const textInput = document.getElementById('seq-rename-input');
    const submitBtn = document.getElementById('submit-btn');
    const form = document.getElementById('seq-rename-form');
    const toggleCheckboxFileRename = document.getElementById('toggle-checkbox-file-rename');
    const fileRenameFormDiv = document.getElementById('file-rename-form-div');

    let isSeqToggle = false;
    let isFormSubmitted = false;





    let new_name = '';
    var dictString = document.getElementById('uploaded_files_name').textContent.trim();
    var uploadedFilesName = JSON.parse(dictString.replace(/'/g, '"'));

    document.getElementById('file-input').addEventListener('change', function() {
        const uploadMessage = document.querySelector('.upload-message');
        if (this.files && this.files.length > 0) {
            uploadMessage.textContent = 'File selected: ' + this.files[0].name;
        } else {
            uploadMessage.textContent = 'Click the button to upload the file with a specific list';
        }
    });
    
    console.log(toggleCheckbox);


    const seqRenameCheckbox = document.getElementById('toggle-checkbox');
    const fileRenameCheckbox = document.getElementById('toggle-checkbox-file-rename');
    const seqRenameForm = document.getElementById('seq-rename-form');

    setTimeout(checkSeqToggleStatus, 0);
    function handleToggle(currentCheckbox, otherCheckbox, showForm, hideForm) {
        if (currentCheckbox.checked) {
            otherCheckbox.checked = false;
            showForm.classList.remove('hidden');
            hideForm.classList.add('hidden');
            setTimeout(checkSeqToggleStatus, 0);
        } else {
            showForm.classList.add('hidden');
            setTimeout(checkSeqToggleStatus, 0);
        }
    }

    seqRenameCheckbox.addEventListener('change', () => handleToggle(seqRenameCheckbox, fileRenameCheckbox, seqRenameForm, fileRenameFormDiv));
    fileRenameCheckbox.addEventListener('change', () => handleToggle(fileRenameCheckbox, seqRenameCheckbox, fileRenameFormDiv, seqRenameForm));


    // setTimeout(checkSeqToggleStatus, 0);
    toggleCheckbox.addEventListener('change', () => {
        if (toggleCheckbox.checked) {
            isSeqToggle = true;
        } else {
            isSeqToggle = false;
        }
        setTimeout(checkSeqToggleStatus, 0);
    });


    form.addEventListener('submit', (event) => {
        event.preventDefault();
        new_name = textInput.value;
        isFormSubmitted = true;
        setTimeout(checkSeqToggleStatus, 0);
    });

    function checkSeqToggleStatus() {
        let renamed_dict;
        if (isSeqToggle && isFormSubmitted) {
            console.log('Sequence renaming enabled');
            renamed_dict = updateDictionaryValuesWithSuffix(uploadedFilesName, new_name);
            console.log("renamed_dict isSeqToggle",renamed_dict);
        } else {
            console.log('Sequence renaming disabled');
            renamed_dict = uploadedFilesName
            console.log("renamed_dict isSeqNotToggle",renamed_dict);
        }
        generateTableFromDictionary(renamed_dict);
    }


    function updateDictionaryValuesWithSuffix(dictionary, baseText) {
        var updatedDictionary = {};
        var count = 1;
        console.log("dictionary inside value with sufix",dictionary);
        for (var key in dictionary) {
            if (dictionary.hasOwnProperty(key)) {
                var fileExtension = dictionary[key].split('.').pop();
                updatedDictionary[key] = count + '_' + baseText + '.' + fileExtension;
                count++;
            }
        }
        return updatedDictionary;
    }


    function generateTableFromDictionary(dict) {
        console.log("Table generate function");
        console.log("dict inside table", dict);
        var tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = '';
    
        for (var key in dict) {
            if (dict.hasOwnProperty(key)) {
                var row = document.createElement('tr');
                var keyCell = document.createElement('td');
                var valueCell = document.createElement('td');
                keyCell.textContent = key;
                valueCell.innerHTML = `<input type="text" name="${key}" value="${dict[key]}" placeholder="Enter new name" class="rename-input">`;
                row.appendChild(keyCell);
                row.appendChild(valueCell);
                tableBody.appendChild(row);
            }
        }
    
        // Add event listeners to update the dictionary on input change
        const renameInputs = document.querySelectorAll('.rename-input');
        renameInputs.forEach(input => {
            input.addEventListener('input', function() {
                dict[input.name] = input.value;
                console.log(dict); // Optional: Print updated dictionary to console
            });
        });
    }

    function updateDictionary(event) {
        const input = event.target;
        const key = input.name;
        const value = input.value;
        const tableBody = document.getElementById('tableBody');
        const renamed_dict = {};
        tableBody.querySelectorAll('tr').forEach(row => {
            const keyCell = row.children[0].textContent;
            const valueInput = row.children[1].children[0];
            renamed_dict[keyCell] = valueInput.value;
        });
        console.log("Updated renamed_dict", renamed_dict);
    }
});