// ==UserScript==
// @name     Radarr: Plex scan
// @version  1
// @include  https://k33k00.com/radarr/activity/history
// ==/UserScript==


const serverUrl = "https://home.k33k00.com/scan";


function reqListener() {
    console.log(this.responseText);
}


function sendScanRequest(path) {
    let url = `${serverUrl}?remote_file_path=${path}`;
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

console.log("Initializing Userscript - Radarr: Plex scan");
waitForElementToDisplay(".dl-horizontal > dd:nth-child(6)", 1000);