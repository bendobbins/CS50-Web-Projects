document.addEventListener("DOMContentLoaded", function() {
    if (document.querySelector("#select-sport") != null) {
        document.querySelector("#select-sport").addEventListener('click', toggle_sports);
    }
    if (document.querySelector("#image-upload") != null) {
        document.querySelector("#picture").addEventListener('click', upload_image);
    }
});

function get_csrf() {
    if (!document.cookie) {
        return null;
    }

    var cookieValue = null;

    const cookies = document.cookie.split(';');
    for (let index = 0; index < cookies.length; index++) {
        var cookie = cookies[index].trim();
        // Find csrf token cookie and return it
        if (cookie.substring(0, 10) === ('csrftoken=')) {
            cookieValue = decodeURIComponent(cookie.substring(10));
            break;
        }
    }
    return cookieValue;
}

function toggle_sports() {
    var sports = document.getElementById("sports");
    if (sports.style.display === 'none') {
        sports.style.display = 'block';
    }
    else {
        sports.style.display = 'none';
    }
    return false;
}

function upload_image() {
    document.querySelector("#image-upload").click();
    document.querySelector("#image-upload").onchange = function() {
        document.querySelector("#image-form").submit();
    }
    return false;
}