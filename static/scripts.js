function formSubmit(event) {
  /**
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

  // Send the request, then retrieve/update control current values to reflect
  // the changes.
  sendRequest(formData);
  updateControlValues(updateCurrent=true);
}


function sendRequest(formData) {
  /**
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


function updateControlValues(current=false, set=false) {
  /**
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

    if (current) {
      updateCurrentValueElements(response);
    }

    if (set) {
      updateSetValueElements(response);
    }
  };
}


function updateCurrentValueElements(newValues) {
  console.log(newValues);
  for (let controlName in newValues) {
    let currentValueElement = document.getElementsByClassName(
      "current-value " + controlName
    )[0];

    if (currentValueElement) {
      let newValue = newValues[controlName];
      if (typeof(newValue) === typeof(true)) {
        console.log(currentValueElement);
        if (newValue) {
          currentValueElement.setAttribute("checked", "");
        } else {
          currentValueElement.removeAttribute("checked");
        }
      } else {
        currentValueElement.textContent = newValue;
      }
    }
  }
}


function updateSetValueElements(newValues) {
  for (let controlName in newValues) {
    let setValueElement = document.getElementsByClassName(
      "set " + controlName
    )[0];

    if (setValueElement) {
      let newValue = newValues[controlName];
      if (typeof(newValue) === typeof(true)) {
        console.log(setValueElement);
        if (newValue) {
          setValueElement.setAttribute("checked", "");
        } else {
          setValueElement.removeAttribute("checked");
        }
      } else {
        setValueElement.textContent = newValue;
      }
    }
  }
}


function init() {
  form = document.getElementById("controls");
  form.addEventListener("submit", formSubmit);
  updateControlValues(updateCurrent=true, updateSet=true);
}


init();
