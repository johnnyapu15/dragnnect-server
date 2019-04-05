var canvas = document.getElementById('canvas_view');
var ctx = canvas.getContext('2d');
var data = {};
var painting = document.getElementById('canvas');
var paint_style = getComputedStyle(painting);
canvas.width = parseInt(paint_style.getPropertyValue('width'));
canvas.height = parseInt(paint_style.getPropertyValue('height'));
var rect = canvas.getBoundingClientRect();
var start_time = 0;
// var devicePixelRatio = window.devicePixelRatio || 1;
// dpi_x = document.getElementById('testdiv').offsetWidth * devicePixelRatio;
// dpi_y = document.getElementById('testdiv').offsetHeight * devicePixelRatio;
dpi_x = 0;
dpi_y = 0;

var mouse = {x: 0, y: 0};
var touches = {x: 0, y: 0};
canvas.addEventListener('mousemove', function(e) {
  mouse.x = e.pageX - rect.left;
  mouse.y = e.pageY - rect.top;
}, false);

ctx.lineWidth = 3;
ctx.lineJoin = 'round';
ctx.lineCap = 'round';
ctx.strokeStyle = '#5A6068';

canvas.addEventListener('mousedown', function(e) {
    ctx.beginPath();
    ctx.moveTo(mouse.x, mouse.y);
    getData();
    data['start_x'] = mouse.x;
    data['start_y'] = mouse.y;
    start_time = Date.now();
    canvas.addEventListener('mousemove', onPaint, false);
}, false);
 
canvas.addEventListener('mouseup', function() {
    canvas.removeEventListener('mousemove', onPaint, false);
    data['end_x'] = mouse.x;
    data['end_y'] = mouse.y;
    data['delta'] = Date.now() - start_time;
    //data['pnts'] = pnts;
    data['11pnts'] = get11Pnts(pnts);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    socket.emit('device_update', data)
}, false);

canvas.addEventListener('touchstart', function(evt) {
  evt.preventDefault();
  ctx.beginPath();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;
  ctx.moveTo(touches.x, touches.y);
  getData();
  data['start_x'] = touches.x;
  data['start_y'] = touches.y;
  start_time = Date.now();
  canvas.addEventListener('touchmove', onTouchPaint, false);
}, false);

canvas.addEventListener('touchend', function(evt) {
  evt.preventDefault();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;

  canvas.removeEventListener('touchmove', onTouchPaint, false);
  data['end_x'] = touches.x;
  data['end_y'] = touches.y;
  //data['pnts'] = pnts;
  tmp = get11Pnts(pnts);
  if (tmp[0][0] != -1) {
    data['11pnts'] = tmp;
    data['delta'] = Date.now() - start_time;
    socket.emit('device_update', data);
  }
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}, false);

var onTouchPaint = function(evt) {
  evt.preventDefault();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;
  ctx.lineTo(touches.x, touches.y);
  pnts.push([touches.x, touches.y, Date.now()-start_time]);
  ctx.stroke();
};

function getData() {
  pnts = [];
  data = {};
  data['dpi_x'] = dpi_x;
  data['dpi_y'] = dpi_x;
  data['w'] = window.outerWidth;
  data['width'] = canvas.clientWidth;
  //data['height'] = canvas.clientHeight;
  data['height'] = canvas.clientWidth * window.outerHeight / window.outerWidth;
}
 
var onPaint = function() {
    ctx.lineTo(mouse.x, mouse.y);
    pnts.push([mouse.x, mouse.y, Date.now()-start_time]);
    ctx.stroke();
};

function get11Pnts(arr) {
  ret = [];
  if (arr.length < 10) {
    alert("Plz push reset btn and Draw long line!");
    ret.push([-1, -1, -1]);
    return ret;
  }
  else {
    tmp = arr.length / 10.0;
    for (i = 0; i < 10; i++) {
      ret.push(arr[parseInt(tmp * i)]);
    }
    ret.push(arr[arr.length - 1]);
  }
  return ret;
}

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