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
    $('#sponsorid').hide();
    $('#sponsorid').removeAttr('required');
    $('#sponsorid').removeAttr('data-error');
    $('#title').show();
    $('#title').attr('required', '');
    $('#title').attr('data-error', 'This field is required.');
  }else if ($(this).val() == "driver") {
    $('#title').hide();
    $('#title').removeAttr('required');
    $('#title').removeAttr('data-error');
    $('#sponsorid').show();
  } else {
    $('#sponsorid').hide();
    $('#sponsorid').removeAttr('required');
    $('#sponsorid').removeAttr('data-error');
    $('#title').hide();
    $('#title').removeAttr('required');
    $('#title').removeAttr('data-error');
  }
});

// Suspend User
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

// Unsuspend User
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

// Remove user
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

// Remove user from sponsor
$(function() {
  $(document).on('click', '#removeFromSponsor', function(e) {
    var user =  $(this).attr("name")
    var sponsor = $(this).attr('class');
    $.ajax({ 
      contentType: "charset=utf-8",
      url: '/removeFromSponsor', 
      type: 'POST', 
      data:{'user': user, 'sponsor': sponsor}
    })
  });
});

// Add points
$(function() {
  $(document).on('click', '#addpoints', function(e) {
    var user =  $(this).attr("name")
    var sponsor = $(this).attr('class');
    var points = document.getElementById("addpoints" + user + sponsor).value;
    $.ajax({ 
      contentType: "application/x-www-form-urlencoded",
      url: '/addpts', 
      type: 'POST', 
      data:{'user': user, 'points': points, 'sponsor': sponsor}
    })
  });
});

// Theme code
$("#themeSelect").change(function() {
  if ($(this).val() == "dark") {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme4');
    document.cookie = 'theme=dark'
  } else if ($(this).val() == "red") {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme4');
    document.cookie = 'theme=red'
  } else if ($(this).val() == "clemson") {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme4');
    document.cookie = 'theme=clemson'
  } else if ($(this).val() == "seizure") {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme4');
    document.cookie = 'theme=seizure'
  } else {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme4');
    document.cookie = 'theme=light'
  }
  document.documentElement.style.setProperty('--main-theme1', color1);
  document.documentElement.style.setProperty('--main-theme2', color2);
  document.documentElement.style.setProperty('--main-theme3', color3);
  document.documentElement.style.setProperty('--main-theme4', color4);
});

function setThemeFromCookie() {
  if (document.cookie.match(/theme=dark/i) != null) {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--dark-theme4');
  } else if (document.cookie.match(/theme=red/i) != null) {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--red-theme4');
  } else if (document.cookie.match(/theme=clemson/i) != null) {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--clemson-theme4');
  } else if (document.cookie.match(/theme=seizure/i) != null) {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme1');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--seizure-theme4');
  } else {
    var color1 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme');
    var color2 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme2');
    var color3 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme3');
    var color4 = getComputedStyle(document.documentElement).getPropertyValue('--blue-theme4');
  }
  document.documentElement.style.setProperty('--main-theme1', color1);
  document.documentElement.style.setProperty('--main-theme2', color2);
  document.documentElement.style.setProperty('--main-theme3', color3);
  document.documentElement.style.setProperty('--main-theme4', color4);
}

jQuery(function() {
  jQuery('#sponsorSelect').change(function() {
      this.form.submit();
  });
});

// Fix URL and add theme
$(document).ready(function(){
	var uri = window.location.toString();
	if (uri.indexOf("?") > 0) {
	    var clean_uri = uri.substring(0, uri.indexOf("?"));
	    window.history.replaceState({}, document.title, clean_uri);
  }
  setThemeFromCookie()
});





