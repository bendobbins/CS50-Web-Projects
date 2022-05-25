document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector("#follow") != null) {
        // Event listener on follow button
        document.querySelector("#follow").addEventListener('click', follow);
    }

    const edits = document.getElementsByName("edit");
    if (edits != null) {
        // Add event listeners on all edit buttons
        for (let index = 0; index < edits.length; index++) {
            edits[index].addEventListener('click', () => edit(edits[index]));
        }
    }

    const likes = document.getElementsByName("like");
    if (likes != null) {
        // Add event listeners on all like buttons
        for (let index = 0; index < likes.length; index++) {
            likes[index].addEventListener('click', () => like(likes[index]));
        }
    }
});

/*
get_csrf() function comes from anonymous user on stackoverflow
https://stackoverflow.com/questions/43606056/proper-django-csrf-validation-using-fetch-post-request
*/
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

function follow() {
    var followButton = document.querySelector("#follow");

    // Send post request to /following with name of user being followed/unfollowed
    fetch("/following", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "X-CSRFToken": get_csrf()
        },
        body: JSON.stringify({
            followed: document.querySelector("#profile-user").value
        })
    })
    .then(response => response.json())
    .then(result => {
        // Update follow button and follower count according to response from server
        if (result.followed) {
            followButton.innerHTML = "Unfollow";
        } else if (result.unfollowed) {
            followButton.innerHTML = "Follow";
        } else {
            alert("Invalid follow")
        }

        if (result.followers != null) {
            document.querySelector("#followers").innerHTML = result.followers;
        }
    });
}

function edit(editButton) {
    if (document.getElementById(editButton.value) != null) {
        // Get content of post (span has same id as post, which is same as editButton value)
        var content = document.getElementById(editButton.value).innerHTML;
    } else {
        return;
    }

    // Replace span for content of post with textarea that has content preloaded into it
    const textarea = document.createElement("textarea");
    textarea.classList.add("edit-text");
    textarea.innerHTML = content;
    document.getElementById(editButton.value).replaceWith(textarea);
    editButton.innerHTML = "Save";

    // Save button clicked
    editButton.onclick = function () {
        // Create new edit button and new content span, replace old edit button and textarea respectively
        const newContent = textarea.value;
        const newSpan = document.createElement("span");
        const newButton = document.createElement("button");
        newButton.classList.add("btn", "btn-sm", "btn-outline-primary");
        newButton.innerHTML = "Edit";
        newButton.name = "edit";
        newButton.value = editButton.value;
        newSpan.id = editButton.value;
        newSpan.innerHTML = newContent;
        textarea.replaceWith(newSpan);
        editButton.replaceWith(newButton);
        newButton.addEventListener('click', () => edit(newButton));

        // Send put request to edit so that server can replace old content of post with new content of post
        fetch("/edit", {
            method: "PUT",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "X-CSRFToken": get_csrf()
            },
            body: JSON.stringify({
                // Include post id and new content
                id: newButton.value,
                content: newContent
            })
        })
        .then(response => response.json())
        .then(result => {
            // If invalid request, display error alert and reload
            if (result.error != null) {
                window.location.reload();
                alert(result.error);
            }
        });
        return false;
    }
}

function like(likeButton) {
    var liked = null;
    // Likes count of post with selected button
    var likes = document.getElementById("like " + likeButton.value);

    // Change like button text and like count according to whether user has already liked post or not
    if (likeButton.innerHTML == "♡") {
        likeButton.innerHTML = "❤";
        likes.innerHTML = parseInt(likes.innerHTML) + 1;
        liked = true;
    } else {
        likeButton.innerHTML = "♡";
        likes.innerHTML = parseInt(likes.innerHTML) - 1;
        liked = false;
    }

    // Send post request to /like with id of post and whether it was liked or unliked
    fetch("/like", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",
            "X-CSRFToken": get_csrf()
        },
        body: JSON.stringify({
            id: likeButton.value,
            liked: liked
        })
    })
    .then(response => response.json())
    .then(result => {
        // If something went wrong, display error alert and reload
        if (result.error != null) {
            window.location.reload();
            alert(result.error);
        }
    });
}