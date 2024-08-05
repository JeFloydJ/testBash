var retryCount = 0; // retry counter
const maxRetries = 30; // max number of retries
const baseDelay = 500; // initial delay

function startTransfer() {
    $('#loading').show(); // show view in loading page
    var progress = 0; // set progress to 0%
    var interval = setInterval(function() {
        progress += 1; // increment progress by 1
        $('#progress').text(progress + '%'); // update progress text

        // if progress is greater than 100
        if (progress >= 100) clearInterval(interval);
    }, 2000); // Update progress every 2 seconds

    $.ajax({ // start polling
        url: '/transferData',
        type: 'GET',
        success: function(response) {
            if (response.status === 200) {
                setTimeout(function() { pollServer(interval); }, baseDelay);
            } else {
                clearInterval(interval);
                $('#loading').hide();
                alert('Error starting the transfer process: ' + response.message);
            }
        },
        error: function(xhr, status, error) {
            clearInterval(interval);
            $('#loading').hide();
            alert('Error starting the transfer process: ' + xhr.responseText);
        }
    });  
}

function pollServer(interval) {
    $.ajax({
        url: '/Validator',
        type: 'GET',
        success: function(response) {
            if (response.status === 200) {
                clearInterval(interval); // stop the interval when data transfer is finished
                $('#loading').hide(); // hide the loading view
                location.href = '/'; // redirect to main page
                retryCount = 0; // reset retry counter
            } else if (response.status === 'in_progress') {
                // if transfer is not complete, send request to server
                if (retryCount < maxRetries) {
                    retryCount++;
                    const delay = baseDelay * Math.pow(2, retryCount); // increment exponential retry
                    setTimeout(function() { pollServer(interval); }, delay);
                }
            } else if (response.status === 'error') {
                clearInterval(interval); // stop interval if there's an error
                $('#loading').hide(); // hide loading view
                alert('Error during data transfer: ' + response.message); // show error message
            }
        },
        error: function(xhr, status, error) {
            clearInterval(interval); // stop interval if there's an error
            $('#loading').hide(); // hide loading view
            alert('Error transferring data: ' + xhr.responseText); // show error message
        }
    });
}