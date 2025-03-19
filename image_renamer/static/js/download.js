document.addEventListener('DOMContentLoaded', function() {

    var downloadButton = document.getElementById('downloadButton')
    var messageDiv = document.getElementById('success-message')
    var messageDict = document.getElementById('success-message').textContent.trim();
    var responseData = JSON.parse(messageDict.replace(/'/g, '"'));

    if (messageDiv) {
        messageDiv.innerHTML = responseData.message;
        if (responseData.status === 'success') {
            messageDiv.style.backgroundColor = '#4CAF50';
        } else if (responseData.status === 'error') {
            messageDiv.style.backgroundColor = '#cc0000';
            downloadButton.style.display='none';
        }

        messageDiv.style.display = 'block';
        setTimeout(() => {
            messageDiv.classList.add('show');
        }, 10);

        // Hide the message after 5 seconds (5000 milliseconds)
        setTimeout(() => {
            messageDiv.classList.remove('show');
            messageDiv.style.display = 'none';
        }, 5000);
    }
});