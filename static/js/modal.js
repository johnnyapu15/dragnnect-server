var modalWin = document.getElementById("modalWindow");
var modalBtn = document.getElementById("modalBtn");
var span = document.getElementsByClassName("close")[0];
var modalInput = "default";

function modalOpen() {
    modalWin.style.display = "block";
}

function sendExp() {
    modalWin.style.display = "none";
    sendMsg({
        m: "sendingExpNum",
        data: modalInput
    });
}
sendExp();
span.onclick = function() {
    sendExp();
}

window.onclick = function(event) {
    if (event.target == modalWin) {
        sendExp();
    }
}

// window.addEventListener("mousedown", function(evt) {
//     if (evt.target == modalWin) {
//         sendExp();
//     }
// })

// window.addEventListener("touchstart", function(evt) {
//     if (evt.target == modalWin) {
//         sendExp();
//     }
// })

