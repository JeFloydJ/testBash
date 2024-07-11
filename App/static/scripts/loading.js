var retryCount = 0; //retry counter
const maxRetries = 30; //max number of retry
const baseDelay = 500; //initial delay

function startTransfer() {
    $('#loading').show(); // show view in loading page
    var progress = 0; //set progress in 0%
    var interval = setInterval(function() {
        progress += 1; // increment process in +1
        $('#progress').text(progress + '%'); // update progress text

        // if progress is greather than 100
        if (progress >= 100) clearInterval(interval);
    }, 2000); // Actualiza el progreso cada 2 segundos

    $.ajax({ //start polling
        url: '/transferData',
        type: 'GET',
        success: function(response) {
            console.log(response, interval)
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
            if (response.status == 200) {
                clearInterval(interval); // stop the interval when data transfer is finished
                $('#loading').hide(); // hidden view of loading
                location.href = '/'; //redirect main page
                retryCount = 0; // set counter of retrys
            } else {
                // if transfer is not complete , send request to server
                if (retryCount < maxRetries) {
                    retryCount++;
                    const delay = baseDelay * Math.pow(2, retryCount); //increment exponential retry
                    setTimeout(function() { pollServer(interval); }, delay);
                }
            }
        },
        error: function(error) {
            clearInterval(interval); //interval if exists some error
            $('#loading').hide(); // hidden view of loading
            alert('Error al transferir data'); // message of error
        }
    });
}