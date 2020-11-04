$("#sendmessage").click(function(){
  //location.reload();
});

$("#showcompose").click(function(){
  $("#hide").toggle();
});

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