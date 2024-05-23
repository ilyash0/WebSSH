function connect(host, username, password) {
    show_loading_indicator();

    const XHR = new XMLHttpRequest();
    XHR.open("POST", "/connect");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    XHR.onreadystatechange = function () {
        console.log(XHR.status)
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 200) {
            document.location.href = "/panel"
        } else if (XHR.status >= 400) {
            document.getElementById("alert-box").classList.add("alert-warning")
            document.getElementById("alert-box").innerText = `Ошибка ${XHR.status}: ${JSON.parse(XHR.responseText).detail}`
        }
        hide_loading_indicator();
    };
    XHR.send("host=" + host + "&username=" + username + "&password=" + password + "");
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

function send_reboot() {
    const XHR = new XMLHttpRequest();
    XHR.open("POST", "/reboot");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    XHR.onreadystatechange = function () {
        const ALERT_BOX = document.getElementById("alert-box")
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 200) {
            ALERT_BOX.classList.add("alert-success")
            ALERT_BOX.innerText = `Машина успешно перезагружена. Соединение оборвано`
        } else if (XHR.status >= 400) {
            ALERT_BOX.classList.add("alert-warning")
            ALERT_BOX.innerText = `Ошибка ${XHR.status}: ${JSON.parse(XHR.responseText).detail}`
        }
    };
    XHR.send();
}

function disconnect() {
    const XHR = new XMLHttpRequest();
    XHR.open("GET", "/disconnect");
    XHR.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    XHR.onreadystatechange = function () {
        const ALERT_BOX = document.getElementById("alert-box")
        if (XHR.readyState === XMLHttpRequest.DONE && XHR.status === 200) {
            document.location.href = "/"
        } else if (XHR.status >= 400) {
            ALERT_BOX.classList.add("alert-warning")
            ALERT_BOX.innerText = `Ошибка ${XHR.status}: ${JSON.parse(XHR.responseText).detail}`
        }
    };
    XHR.send();
}


