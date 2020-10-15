/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function updateNav() {
  var x = document.getElementById("sidebar");
  if (x.className === "side-navbar") {
    x.className += " responsive";
  } else {
    x.className = "side-navbar";
  }
}

$("#roleSelect").change(function() {
  if ($(this).val() == "sponsor") {
    $('#title').show();
    $('#title').attr('required', '');
    $('#title').attr('data-error', 'This field is required.');
  } else {
    $('#title').hide();
    $('#title').removeAttr('required');
    $('#title').removeAttr('data-error');
  }
});

$(function() {
  $(document).on('click', '#suspend', function(e) {
    var user =  $(this).attr("name")
    $.ajax({ 
      contentType: "charset=utf-8",
      url: '/suspend', 
      type: 'POST', 
      data: user
    })
  });
});

$(function() {
  $(document).on('click', '#unsuspend', function(e) {
    var user =  $(this).attr("name")
    $.ajax({ 
      contentType: "charset=utf-8",
      url: '/unsuspend', 
      type: 'POST', 
      data: user
    })
  });
});

$(function() {
  $(document).on('click', '#remove', function(e) {
    var user =  $(this).attr("name")
    $.ajax({ 
      contentType: "charset=utf-8",
      url: '/remove', 
      type: 'POST', 
      data: user
    })
  });
});

$(document).ready(function(){
	var uri = window.location.toString();
	if (uri.indexOf("?") > 0) {
	    var clean_uri = uri.substring(0, uri.indexOf("?"));
	    window.history.replaceState({}, document.title, clean_uri);
	}
});