
var socket = io.connect('http://' + document.domain + ':' + location.port);
      
socket.on('update', function(data) {
count = data.count;
document.getElementById("textarea").innerHTML = "#Room: " + room_id + "\nDev Number: " + count;
});
data = {};

socket.on('connect', function() {
socket.emit('join', data);
});

function leave() {
socket.emit('leave');
history.back();
};

socket.on('ntp_0', function() {
t1 = Date.now();
socket.emit('ntp_1', t1);
});

function resetLines() {
    socket.emit('reset_lines');
}

//socket.on('connect', function() {

//});
socket.on('redirect', function (data) {
window.location = data.url;
});