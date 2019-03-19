var canvas = document.getElementById('canvas_view');
var ctx = canvas.getContext('2d');
 
var painting = document.getElementById('canvas');
var paint_style = getComputedStyle(painting);
canvas.width = parseInt(paint_style.getPropertyValue('width'));
canvas.height = parseInt(paint_style.getPropertyValue('height'));

var mouse = {x: 0, y: 0};
 
canvas.addEventListener('mousemove', function(e) {
  mouse.x = e.pageX - this.offsetLeft;
  mouse.y = e.pageY - this.offsetTop;
}, false);

ctx.lineWidth = 3;
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.strokeStyle = '#00ac00';
var data = {};
canvas.addEventListener('mousedown', function(e) {
    ctx.beginPath();
    ctx.moveTo(mouse.x, mouse.y);
    data = {};
    data['width'] = window.outerWidth;
    data['height'] = window.outerHeight;
    data['start_x'] = mouse.x;
    data['start_y'] = mouse.y;
    data['start_time'] = Date.now();
    canvas.addEventListener('mousemove', onPaint, false);
}, false);
 
canvas.addEventListener('mouseup', function() {
    canvas.removeEventListener('mousemove', onPaint, false);
    data['end_x'] = mouse.x;
    data['end_y'] = mouse.y;
    data['end_time'] = Date.now();
    // var http = new XMLHttpRequest();
    // http.open('POST', "callback", true);
    // http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    // http.send(JSON.stringify(data));
    socket.emit('device_update', data)
}, false);


canvas.addEventListener('touchstart', function(evt) {
  ctx.beginPath();
  var touches = evt.changedTouches;

  ctx.moveTo(touches[0].pageX, touches[0].pageY);
  data = {};
  data['width'] = window.outerWidth;
  data['height'] = window.outerHeight;
  data['start_x'] = touches[0].pageX;
  data['start_y'] = touches[0].pageY;
  data['start_time'] = Date.now();
  canvas.addEventListener('touchmove', onTouchPaint, false);
}, false);

canvas.addEventListener('touchend', function(evt) {
  var touches = evt.changedTouches;

  canvas.removeEventListener('touchmove', onTouchPaint, false);
  data['end_x'] = touches[0].pageX;
  data['end_y'] = touches[0].pageY;
  data['end_time'] = Date.now();
  socket.emit('device_update', data)
}, false);

var onTouchPaint = function(evt) {
  var touches = evt.changedTouches;
  ctx.lineTo(touches[0].pageX, touches[0].pageY);
  ctx.stroke();
};

 
var onPaint = function() {
    ctx.lineTo(mouse.x, mouse.y);
    ctx.stroke();
};


// window.addEventListener("beforeunload", function (evt) {
//   // var http = new XMLHttpRequest();
//   // http.open('POST', "quit", true);
//   // http.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
//   // data = {};
//   // data['id'] = room_id;
//   // data['count'] = count;
//   // http.send(JSON.stringify(data));
//   // var socket = io.connect('http://' + document.domain + ':' + location.port);
//   // data = {};
//   // data['id'] = room_id;
//   // data['count'] = count;
//   socket.emit('leave', {data: data});
// });