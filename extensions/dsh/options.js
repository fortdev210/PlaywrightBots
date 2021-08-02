// Saves options to chrome.storage
function save_options() {
  
  enabledSuppliers = [];
  
  for (var i = 0; i < document.querySelectorAll('input[name="supplier_choice"][type="checkbox"]').length; i++) {
    if (document.querySelectorAll('input[name="supplier_choice"][type="checkbox"]')[i].checked === true) {
      enabledSuppliers.push(document.querySelectorAll('input[name="supplier_choice"][type="checkbox"]')[i].value);
    }
  }
  
  localStorage.supplierProxies = enabledSuppliers;
  
  if (document.querySelector('[name=auto_proxy]').checked === true) {
	  localStorage.autoProxy = 'enabled';
  } else {
	  localStorage.autoProxy = 'disabled';
  }
  
  var hostname = document.getElementById('host').value;
  //var likesColor = document.getElementById('like').checked;
  chrome.storage.sync.set({
    host: hostname
    
  }, function() {
    // Update status to let user know options were saved.
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(function() {
      status.textContent = '';
    }, 750);
  });
  loadOptions();
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
  // Use default value 
  chrome.storage.sync.get({
    host: 'admin.stlpro.com'
    
  }, function(items) {
    document.getElementById('host').value = items.host;    
  });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click', save_options);

// Display saved options on page
function loadOptions() {
  ready(function() {
	  
      var enabledSuppliers = localStorage.supplierProxies.split(',');
	  
	  for (var i = 0; i < enabledSuppliers.length; i++) {
		  document.querySelector('[name="supplier_choice"][value="' + enabledSuppliers[i] + '"').checked = true;
	  }
	  
	  if (localStorage.autoProxy == 'enabled') {
		  document.querySelector('[name=auto_proxy]').checked = true;
	  } else {
		  document.querySelector('[name=auto_proxy]').checked = false;
	  }
	  
  });
}
loadOptions();

// Document ready lib
function ready(callback){
    if (document.readyState!='loading') callback();
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    else document.attachEvent('onreadystatechange', function(){
        if (document.readyState=='complete') callback();
    });
}

// "About" modal
// Get the modal
var modal = document.getElementById('aboutExt');

// Get the button that opens the modal
var btn = document.getElementById("aboutBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
};