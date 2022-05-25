document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email(false));
  document.getElementById("compose-form").onsubmit = send_mail;
  document.getElementById("archive").addEventListener('click', archive_email);
  document.getElementById("reply").addEventListener('click', () => compose_email(true));

  // By default, load the inbox
  load_mailbox("inbox");
});

function send_mail() {
  // Post an email with proper values from composition form
  fetch("/emails", {
    method: "POST",
    body: JSON.stringify({
      recipients: document.getElementById("compose-recipients").value,
      subject: document.getElementById("compose-subject").value,
      body: document.getElementById("compose-body").value
    })
  })
  .then(response => response.json())
  .then(result => {
    // If there is an error, make it an alert and keep user on composition form
    if (result.error != null) {
      alert(result.error);
    // Else, alert success message and return user to inbox
    } else {
      load_mailbox("sent");
      alert(result.message);
    }
  });
  return false;
}

function archive_email() {
  // Email id will be in archive button value
  var id = parseInt(document.getElementById("archive").value);

  // Change email.archived to false if unarchiving, true if archiving
  if (document.getElementById("archive").innerHTML == "Archive") {
    fetch(`/emails/${id}`, {
      method: "PUT",
      body: JSON.stringify({
        archived: true
      })
    })
  } else if (document.getElementById("archive").innerHTML == "Unarchive") {
    fetch(`/emails/${id}`, {
      method: "PUT",
      body: JSON.stringify({
        archived: false
      })
    })
  }
  // Reload page to return to inbox and update archived emails (doesn't update properly when calling load_mailbox without reloading page)
  location.reload();
}

function compose_email(reply) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email').style.display = 'none';

  var recipients = document.querySelector("#compose-recipients");
  var subject = document.querySelector("#compose-subject");
  var body = document.querySelector("#compose-body");
  var replyButton = document.getElementById("reply"); 

  if (reply) {
    // Email id will be in reply button value
    fetch(`/emails/${replyButton.value}`)
    .then(response => response.json())
    .then(email => {
      // Put sender of last email in recipients slot
      recipients.value = email.sender;
      // Add Re: to subject if needed, fill in subject slot
      if (email.subject.slice(0, 4) != "Re: ") {
        subject.value = "Re: " + email.subject;
      } else {
        subject.value = email.subject;
      }
      // Fill in body slot with body of last email
      body.value = "\n\nOn " + email.timestamp + " " + email.sender + " wrote: " + email.body;
    });
  } else {
    // Clear out composition fields
    recipients.value = '';
    subject.value = '';
    body.value = '';
  }
}

function view_email(id) {
  document.querySelector('#email').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  
  // Get data for requested email
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    document.getElementById("sender").innerHTML = email.sender;
    // Create a comma separated list of recipients
    var recipients = "";
    for (let index = 0; index < email.recipients.length; index++) {
      recipients += email.recipients[index] + ", ";
    }
    // Determine if email can be archived based on whether sender is user
    let archivable = true;
    fetch("/emails/sent")
    .then(response => response.json())
    .then (emails => {
      if (emails[0].sender === email.sender) {
        archivable = false;
      }
      document.getElementById("recipients").innerHTML = recipients.slice(0, -2);
      document.getElementById("subject").innerHTML = email.subject;
      document.getElementById("timestamp").innerHTML = email.timestamp;
      document.getElementById("body").innerHTML = email.body;
      document.getElementById("reply").value = id;
      var archive = document.getElementById("archive");
      // If button is archivable, show button, else hide button
      if (archivable) {
        archive.style.display = 'inline';
        archive.value = id;
        // Change innerHTML of archive button according to whether email is already archived or not
        if (email.archived) {
          archive.innerHTML = "Unarchive";
        } else {
          archive.innerHTML = "Archive";
        }
      } else {
        archive.style.display = 'none';
      }
      });
    //if (email.sender == document.getElementById("user-email").innerHTML) {
    //  archivable = false;
    //}
    // Slice off ", " at the end of recipients
  });

  // Mark email as read
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true
    })
  })
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email').style.display = 'none';

  // Get emails for certain mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // For each email in mailbox
    for (let index = 0; index < emails.length; index++) {
      // Create a div element, add classes based on whether email has been read
      const element = document.createElement("div");
      if (emails[index].read) {
        element.classList.add("email", "read");
      } else {
        element.classList.add("email");
      }

      // Create span for sender, add to div element
      const sender = document.createElement("span");
      sender.innerHTML = emails[index].sender;
      sender.classList.add("sender");
      element.append(sender);

      // Create span for subject, add to div element
      const subject = document.createElement("span");
      subject.innerHTML = emails[index].subject;
      element.append(subject);

      // Create span for timestamp, add to div element
      const date = document.createElement("span");
      date.innerHTML = emails[index].timestamp;
      date.classList.add("date");
      element.append(date);

      // Make div clickable, send to view_email with email id when clicked
      element.addEventListener("click", function() {
        view_email(emails[index].id);
      });

      // Append div element to emails-view
      document.querySelector("#emails-view").append(element);
    }
  });

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}