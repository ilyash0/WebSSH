function connect(host, username, password) {
    showLoadingIndicator();

    const XHR = new XMLHttpRequest();
    XHR.open("POST", "/connect");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    XHR.onreadystatechange = function () {
        console.log(XHR.status)
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 200) {
            document.location.href = "/panel"
        } else if (XHR.status !== 200) {
            document.getElementById("alert-box").classList.add("alert-warning")
            document.getElementById("alert-box").innerText = `Ошибка ${XHR.status}: ${JSON.parse(XHR.responseText).detail}`
        }
        hideLoadingIndicator();
    };
    XHR.send("host=" + host + "&username=" + username + "&password=" + password + "");
}

function showLoadingIndicator() {
    const LOADING_INDICATOR = document.getElementById("loading-indicator");
    if (LOADING_INDICATOR) {
        LOADING_INDICATOR.style.display = "inline-block";
    }
}

function hideLoadingIndicator() {
    const LOADING_INDICATOR = document.getElementById("loading-indicator");
    if (LOADING_INDICATOR) {
        LOADING_INDICATOR.style.display = "none";
    }
}
