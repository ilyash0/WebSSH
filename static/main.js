async function login(username, password, token) {
    show_loading_indicator();

    const XHR = new XMLHttpRequest();
    XHR.open("POST", "/login");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    XHR.onreadystatechange = async function () {
        const ALERT_BOX = document.getElementById("alert-box")
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 204) {
            document.location.href = "/panel"
        } else if (XHR.status >= 400) {
            ALERT_BOX.classList.remove("hidden");
            ALERT_BOX.classList.add("alert-danger");
            ALERT_BOX.innerText = `Ошибка ${XHR.status}: ${XHR.responseText}`;
        }
        hide_loading_indicator();
    };
    let body = new URLSearchParams({
        'username': username,
        'password': password,
        'client_secret': token
    })
    XHR.send(body);
}

function show_loading_indicator() {
    const LOADING_INDICATOR = document.getElementById("loading-indicator");
    if (LOADING_INDICATOR) {
        LOADING_INDICATOR.style.display = "inline-block";
    }
}

function hide_loading_indicator() {
    const LOADING_INDICATOR = document.getElementById("loading-indicator");
    if (LOADING_INDICATOR) {
        LOADING_INDICATOR.style.display = "none";
    }
}

function logout() {
    const XHR = new XMLHttpRequest();
    XHR.open("GET", "/logout");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    XHR.onreadystatechange = function () {
        const ALERT_BOX = document.getElementById("alert-box")
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 200) {
            document.location.href = "/"
        } else if (XHR.status >= 400) {
            ALERT_BOX.classList.remove("hidden");
            ALERT_BOX.classList.add("alert-danger");
            ALERT_BOX.innerText = `Ошибка ${XHR.status}: ${XHR.responseText}`;
        }
    };
    XHR.send();
}
