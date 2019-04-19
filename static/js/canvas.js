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

function drawing_param_set() {
  ctx_dragnnect.lineWidth = 3;
  ctx_dragnnect.lineJoin = 'round';
  ctx_dragnnect.lineCap = 'round';
  ctx_dragnnect.strokeStyle = '#5A6068';
}


canvas_dragnnect.addEventListener('mousedown', function(e) {
    ctx_dragnnect.beginPath();
    drawing_param_set();
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
    //ctx_dragnnect.clearRect(0, 0, canvas_dragnnect.width, canvas_dragnnect.height);
    socket.emit('device_update', data)
}, false);

canvas_dragnnect.addEventListener('touchstart', function(evt) {
  drawing_param_set();
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
  //ctx_dragnnect.clearRect(0, 0, canvas_dragnnect.width, canvas_dragnnect.height);
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


// var canvas_coord = document.getElementById('coord_view');
// var ctx_coord = canvas_coord.getContext('2d');
// // canvas_dragnnect, ctx_dragnnect.
// // painting, paint_style
// var dragnnect2d_painting = document.getElementById('coord_window');
// var dragnnect2d_paint_style = getComputedStyle(dragnnect2d_painting);
// canvas_coord.width = parseInt(dragnnect2d_paint_style.getPropertyValue('width'));
// canvas_coord.height = parseInt(dragnnect2d_paint_style.getPropertyValue('height'));
var w = canvas_dragnnect.width / 2;
var h = canvas_dragnnect.height / 2;
var data_devs;
var colors = [
  '#0000FF',
  '#00FF00',
  '#FF0000',
  '#FFFF00',
  '#00FFFF',
  '#FF00FF'
]
function coord_param_set() {
  ctx_dragnnect.lineWidth = 3;
  ctx_dragnnect.lineJoin = 'round';
  ctx_dragnnect.lineCap = 'round';
  ctx_dragnnect.strokeStyle = '#9BA1A8';
  ctx_dragnnect.fillStyle = '#9BA1A8';
  ctx_dragnnect.font = "50px Arial";
  ctx_dragnnect.fillStyle = colors[dev_id];
  ctx_dragnnect.fillText(dev_id, 20, 50);
}

socket.on('draw', function(data) {
  ctx_dragnnect.clearRect(0, 0, w*2, h*2);
  data_devs = data;
  coord_param_set();
  dragnnect2d_draw(data_devs);
})

function dragnnect2d_draw(devs) {
    if (canvas_dragnnect.getContext) {
      var i;
      for (var key in devs) {
        var dev = devs[key];
        i = parseInt(key);
        ctx_dragnnect.moveTo(dev[0][0]/10 + w, dev[0][1]/10 + h);
        ctx_dragnnect.beginPath();
        dev.forEach(pnt => {
          ctx_dragnnect.lineTo(pnt[0]/10 + w, pnt[1]/10 + h);
        });
        ctx_dragnnect.strokeStyle = colors[i];
        ctx_dragnnect.fillStyle = colors[i];
        ctx_dragnnect.fill();
        ctx_dragnnect.font = "30px Arial";
        ctx_dragnnect.fillStyle = '#212121';
        ctx_dragnnect.fillText(i, dev[0][0]/10 + w + 10, dev[0][1]/10 + h + 30);
      }
      //ctx_2d_demo.theta =       
      
      // dragnnect2d_ctx.lineTo(100, 75);
      // dragnnect2d_ctx.lineTo(100, 25);
      
    }
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