/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function updateNav() {
    var x = document.getElementById("sidebar");
    if (x.className === "side-navbar") {
      x.className += " responsive";
    } else {
      x.className = "side-navbar";
    }
  }