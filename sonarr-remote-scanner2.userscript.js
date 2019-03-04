// ==UserScript==
// @name     Sonarr: Plex scan 2
// @version  1
// @include  https://k33k00.com/sonarr/series/*
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
            console.log("Sending scan request for "+ e.target.innerText)
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

console.log("Initializing Userscript - Sonarr: Plex scan 2");
waitForElementToDisplay("td.string-cell:nth-child(1)", 1000);