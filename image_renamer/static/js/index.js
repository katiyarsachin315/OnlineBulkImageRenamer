document.addEventListener('DOMContentLoaded', function() {
    var messageDiv = document.getElementById('success-message');
    
    // Check if messageDiv exists and has content
    if (messageDiv && messageDiv.textContent.trim() !== '') {
        var messageDict = messageDiv.textContent.trim();
        var responseData = JSON.parse(messageDict.replace(/'/g, '"'));

        messageDiv.innerHTML = responseData.message;
        
        if (responseData.status === 'success') {
            messageDiv.style.backgroundColor = '#4CAF50';
        } else if (responseData.status === 'error') {
            messageDiv.style.backgroundColor = '#cc0000';
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
