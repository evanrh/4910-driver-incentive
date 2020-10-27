var input = document.querySelector('#sendmessage');
var textarea = document.querySelector('.send-message');

input.addEventListener('click', function () {
    location.reload();
}, false);

function showCompose()
{
    element = document.getElementById('hide')
    if (element.style.display == 'none'){
        element.style.display = 'block';
    } else {
        element.style.display = 'none';
    }
}

$(function() {
    $(document).on('click', '#sendTomessage', function(e) {
      var user =  $(this).attr("name")
      var recipient = document.getElementById("recipient").value;
      var message = document.getElementById("composeMessage").value;
      $.ajax({ 
        contentType: "charset=utf-8",
        url: '/sendto', 
        type: 'POST', 
        data: {'user': user, 'recipient': recipient, 'message': message}
      })
    });
  });