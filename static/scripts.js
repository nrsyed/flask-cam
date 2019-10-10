function formSubmit(event) {
  /*
   * Submit control values to the server.
   */

  event.preventDefault();
  let url = "/submit";
  let request = new XMLHttpRequest();
  let formData = new FormData();

  // Iterate through controls with discrete numerical values.
  let discreteControls = [
    "brightness", "contrast", "exposure", "focus", "saturation", "zoom", "delay"
  ];
  for (let controlName of discreteControls) {
    formData.append(
      controlName,
      document.getElementsByClassName("set " + controlName)[0].value
    );
  }

  // Iterate through checkbox controls.
  let checkboxControls = ["autofocus"];
  for (let controlName of checkboxControls) {
    formData.append(
      controlName,
      document.getElementsByClassName("set " + controlName)[0].checked
    );
  }

  sendRequest(formData);
}


function sendRequest(formData) {
  /*
   * Send a POST request to the server.
   */

  let endpoint_url = "/submit";
  let request = new XMLHttpRequest();
  request.open("POST", endpoint_url, true);
  request.send(formData);
  request.onload = function() {
  	console.log(request.responseText);
  };
  request.onerror = function() {
  	console.log("POST error");
  };
}


function getControlValues(updateSet=false) {
  /*
   * Get the current values of each control from the webcam server and
   * update the value displayed in the "Current value" column on the web
   * page. Optionally, the user-adjustable values in the "Set" column on the
   * web page can be updated as well.
   */

  let endpoint_url = "/get";
  let request = new XMLHttpRequest();
  request.open("GET", endpoint_url, true);
  request.send();
  request.onload = function() {
    let response = JSON.parse(request.responseText);

    // JSON response contains keys corresponding to each control. The HTML
    // element for each "Current value" column belongs to classes
    // `current-value` and the control name, e.g., `saturation`.
    for (let controlName in response) {
      let currValQuery = "current-value " + controlName;
      let currentValueElement = document.getElementsByClassName(currValQuery)[0];
      if (currentValueElement) {
        currentValueElement.textContent = response[controlName];
      }

      // The HTML element for each "Set" column belongs to classes `set` and
      // the control name, e.g., `focus`.
      if (updateSet) {
        let setQuery = "set " + controlName;
        let setElement = document.getElementsByClassName(setQuery)[0];
        if (setElement) {
          setElement.value = response[controlName];
        }
      }
    }
  };
}


function init() {
  form = document.getElementById("controls");
  form.addEventListener("submit", formSubmit);
  getControlValues(updateSet=true);
}


init();
