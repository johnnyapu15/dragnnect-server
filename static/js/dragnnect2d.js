var canvas_coord = document.getElementById('coord_view');
var ctx_coord = canvas_coord.getContext('2d');
 
var dragnnect2d_painting = document.getElementById('coord_window');
var dragnnect2d_paint_style = getComputedStyle(dragnnect2d_painting);
canvas_coord.width = parseInt(dragnnect2d_paint_style.getPropertyValue('width'));
canvas_coord.height = parseInt(dragnnect2d_paint_style.getPropertyValue('height'));
var w = canvas_coord.width / 2;
var h = canvas_coord.height / 2;
var dragnnect2d_mouse = {x: 0, y: 0};
var colors = [
  '#0000FF',
  '#00FF00',
  '#FF0000',
  '#FFFF00',
  '#00FFFF',
  '#FF00FF'
]
// canvas.addEventListener('mousemove', function(e) {
//   mouse.x = e.pageX - this.offsetLeft;
//   mouse.y = e.pageY - this.offsetTop;
// }, false);

ctx_coord.lineWidth = 3;
ctx_coord.lineJoin = 'round';
ctx_coord.lineCap = 'round';
ctx_coord.strokeStyle = '#9BA1A8';
ctx_coord.fillStyle = '#9BA1A8';
var dragnnect2d_data = {};
ctx_coord.font = "50px Arial";
ctx_coord.fillStyle = colors[dev_id];
ctx_coord.fillText(dev_id, 20, 50);
socket.on('draw', function(data) {
  ctx_coord.clearRect(0, 0, w*2, h*2);
  ctx_coord.font = "50px Arial";
  ctx_coord.fillStyle = colors[dev_id];
  ctx_coord.fillText(dev_id, 30, 50);
  dragnnect2d_draw(data);
})

function dragnnect2d_draw(devs) {
    if (canvas_coord.getContext) {
      var i = 0;
      devs.forEach(dev => {
        ctx_coord.moveTo(dev[0][0]/10 + w, dev[0][1]/10 + h);
        ctx_coord.beginPath();
        dev.forEach(pnt => {
          ctx_coord.lineTo(pnt[0]/10 + w, pnt[1]/10 + h);
        });
        ctx_coord.strokeStyle = colors[i];
        ctx_coord.fillStyle = colors[i];
        ctx_coord.fill();
        ctx_coord.font = "30px Arial";
        ctx_coord.fillStyle = '#212121';
        ctx_coord.fillText(i, dev[0][0]/10 + w + 10, dev[0][1]/10 + h + 30);
        
        i++;
      });
      
      
      // dragnnect2d_ctx.lineTo(100, 75);
      // dragnnect2d_ctx.lineTo(100, 25);
      
    }
  }