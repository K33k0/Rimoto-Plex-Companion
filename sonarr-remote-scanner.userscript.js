// ==UserScript==
// @name     Sonarr: Plex scan
// @version  1.0.1
// @include  https://k33k00.com/sonarr/calendar
// @updateURL https://raw.githubusercontent.com/MDCEY/Rimoto_plex_companion/develop/sonarr-remote-scanner.userscript.js
// ==/UserScript==


const serverUrl = "https://home.k33k00.com/scan";


function reqListener() {
    console.log(this.responseText);
}


function sendScanRequest(path) {
    let url = `${serverUrl}?remote_file_path=${encodeURI(path)}`;
    let oReq = new XMLHttpRequest();
    oReq.addEventListener("load", reqListener);
    oReq.open("GET", url);
    oReq.send();
}


function waitForElementToDisplay(selector, time) {
    if (document.querySelector(selector) != null) {
        let elem = document.querySelector(selector);
        elem.addEventListener("click", function (e) {
            sendScanRequest(e.target.innerText)
        });
        waitForElementToDissapear(selector, time)
    } else {
        setTimeout(function () {
            waitForElementToDisplay(selector, time);
        }, time);
    }
}

function waitForElementToDissapear(selector, time) {
    console.log("Waiting for element");
    if (document.querySelector(selector) == null) {
        waitForElementToDisplay(selector, time);
    } else {
        setTimeout(function () {
            waitForElementToDissapear(selector, time);
        }, time);
    }
}

console.log("Initializing Userscript - Sonarr: Plex scan");
waitForElementToDisplay(".string-cell", 1000);