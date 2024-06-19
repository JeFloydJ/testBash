var retryCount = 0; // Retry counter
const maxRetries = 20; // Maximum number of retries
const baseDelay = 500; // Initial delay of 5 seconds

function startTransfer() {
    $('#loading').show(); // Show the loading view
    var progress = 0; // Set progress to 0%
    var interval = setInterval(function() {
        progress += 1; // Increase progress by 1% for each iteration
        $('#progress').text(progress + '%'); // Update the text of the progress element

        // If progress is greater than 100%
        if (progress >= 100) clearInterval(interval);
    }, 5000); // Update the progress every 5 seconds

    $.ajax({ // Start polling
        url: '/transferData',
        type: 'GET',
        success: function(response) {
            console.log(response, interval);
            if (response.status == 200) {
                setTimeout(function() { pollServer(interval); }, baseDelay);
            } 
        }
    });  
}

function pollServer(interval) {
    $.ajax({
        url: '/Validator',
        type: 'GET',
        success: function(response) {
            console.log(response, interval);
            if (response.status == 200) {
                clearInterval(interval); // Stop the interval when data transfer is finished
                $('#loading').hide(); // Hide the loading view
                location.href = '/'; // Redirect to the main page
                retryCount = 0; // Reset the retry counter
            } else {
                // If transfer is not complete, send a request to the server
                if (retryCount < maxRetries) {
                    retryCount++;
                    const delay = baseDelay * Math.pow(2, retryCount); // Increment exponential retry
                    setTimeout(function() { pollServer(interval); }, delay);
                }
            }
        },
        error: function(error) {
            clearInterval(interval); // Clear interval if there is an error
            $('#loading').hide(); // Hide the loading view
            alert('Error transferring data'); // Error message
        }
    });
}
