function formSubmit(event) {
  event.preventDefault();
  let url = "/submit";
  let request = new XMLHttpRequest();
  let formData = new FormData();

  for (input of event.target.querySelectorAll("input")) {
  	formData.append(input.id, input.value);
  }

  sendRequest(formData);
}

function sendRequest(formData) {
  let url = "/submit";
  let request = new XMLHttpRequest();
  request.open("POST", url, true);
  request.send(formData);
  request.onload = function() {
  	console.log(request.responseText);
  };
  request.onerror = function() {
  	console.log("POST error");
  };
}

function getControlValues(updateSet=false) {
  let url = "/get";
  let request = new XMLHttpRequest();
  request.open("GET", url, true);
  request.send();
  request.onload = function() {
    let response = JSON.parse(request.responseText);

    for (let controlName in response) {
      let currValQuery = "current-value " + controlName;
      let currentValueElement = document.getElementsByClassName(currValQuery)[0];
      if (currentValueElement) {
        currentValueElement.textContent = response[controlName];
      }

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
