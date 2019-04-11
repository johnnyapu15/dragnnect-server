var canvas_dragnnect = document.getElementById('canvas_view');
var ctx_dragnnect = canvas_dragnnect.getContext('2d');
var data = {};
var painting = document.getElementById('canvas');
var paint_style = getComputedStyle(painting);
canvas_dragnnect.width = parseInt(paint_style.getPropertyValue('width'));
canvas_dragnnect.height = parseInt(paint_style.getPropertyValue('height'));
var rect = canvas_dragnnect.getBoundingClientRect();
var start_time = 0;
// var devicePixelRatio = window.devicePixelRatio || 1;
// dpi_x = document.getElementById('testdiv').offsetWidth * devicePixelRatio;
// dpi_y = document.getElementById('testdiv').offsetHeight * devicePixelRatio;
dpi_x = 0;
dpi_y = 0;

var mouse = {x: 0, y: 0};
var touches = {x: 0, y: 0};
canvas_dragnnect.addEventListener('mousemove', function(e) {
  mouse.x = e.pageX - rect.left;
  mouse.y = e.pageY - rect.top;
}, false);

ctx_dragnnect.lineWidth = 3;
ctx_dragnnect.lineJoin = 'round';
ctx_dragnnect.lineCap = 'round';
ctx_dragnnect.strokeStyle = '#5A6068';

canvas_dragnnect.addEventListener('mousedown', function(e) {
    ctx_dragnnect.beginPath();
    ctx_dragnnect.moveTo(mouse.x, mouse.y);
    getData();
    data['start_x'] = mouse.x;
    data['start_y'] = mouse.y;
    start_time = Date.now();
    canvas_dragnnect.addEventListener('mousemove', onPaint, false);
}, false);
 
canvas_dragnnect.addEventListener('mouseup', function() {
    canvas_dragnnect.removeEventListener('mousemove', onPaint, false);
    data['end_x'] = mouse.x;
    data['end_y'] = mouse.y;
    data['delta'] = Date.now() - start_time;
    //data['pnts'] = pnts;
    data['11pnts'] = get11Pnts(pnts);
    ctx_dragnnect.clearRect(0, 0, canvas_dragnnect.width, canvas_dragnnect.height);
    socket.emit('device_update', data)
}, false);

canvas_dragnnect.addEventListener('touchstart', function(evt) {
  evt.preventDefault();
  ctx_dragnnect.beginPath();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;
  ctx_dragnnect.moveTo(touches.x, touches.y);
  getData();
  data['start_x'] = touches.x;
  data['start_y'] = touches.y;
  start_time = Date.now();
  canvas_dragnnect.addEventListener('touchmove', onTouchPaint, false);
}, false);

canvas_dragnnect.addEventListener('touchend', function(evt) {
  evt.preventDefault();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;

  canvas_dragnnect.removeEventListener('touchmove', onTouchPaint, false);
  data['end_x'] = touches.x;
  data['end_y'] = touches.y;
  //data['pnts'] = pnts;
  tmp = get11Pnts(pnts);
  if (tmp[0][0] != -1) {
    data['11pnts'] = tmp;
    data['delta'] = Date.now() - start_time;
    socket.emit('device_update', data);
  }
  ctx_dragnnect.clearRect(0, 0, canvas_dragnnect.width, canvas_dragnnect.height);
}, false);

var onTouchPaint = function(evt) {
  evt.preventDefault();
  touches.x = evt.changedTouches[0].pageX;
  touches.y = evt.changedTouches[0].pageY - rect.top;
  ctx_dragnnect.lineTo(touches.x, touches.y);
  pnts.push([touches.x, touches.y, Date.now()-start_time]);
  ctx_dragnnect.stroke();
};

function getData() {
  pnts = [];
  data = {};
  data['dpi_x'] = dpi_x;
  data['dpi_y'] = dpi_x;
  data['w'] = window.outerWidth;
  data['width'] = canvas_dragnnect.clientWidth;
  //data['height'] = canvas.clientHeight;
  data['height'] = canvas_dragnnect.clientWidth * window.outerHeight / window.outerWidth;
}
 
var onPaint = function() {
    ctx_dragnnect.lineTo(mouse.x, mouse.y);
    pnts.push([mouse.x, mouse.y, Date.now()-start_time]);
    ctx_dragnnect.stroke();
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