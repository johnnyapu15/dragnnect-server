var dragnnect2d_canvas = document.getElementById('coord_view');
var dragnnect2d_ctx = dragnnect2d_canvas.getContext('2d');
 
var dragnnect2d_painting = document.getElementById('coord_window');
var dragnnect2d_paint_style = getComputedStyle(dragnnect2d_painting);
dragnnect2d_canvas.width = parseInt(dragnnect2d_paint_style.getPropertyValue('width'));
dragnnect2d_canvas.height = parseInt(dragnnect2d_paint_style.getPropertyValue('height'));
var w = dragnnect2d_canvas.width / 2;
var h = dragnnect2d_canvas.height / 2;
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

dragnnect2d_ctx.lineWidth = 3;
dragnnect2d_ctx.lineJoin = 'round';
dragnnect2d_ctx.lineCap = 'round';
dragnnect2d_ctx.strokeStyle = '#9BA1A8';
dragnnect2d_ctx.fillStyle = '#9BA1A8';
var dragnnect2d_data = {};
dragnnect2d_ctx.font = "50px Arial";
dragnnect2d_ctx.fillStyle = colors[dev_id];
dragnnect2d_ctx.fillText(dev_id, 20, 50);
socket.on('draw', function(data) {
  dragnnect2d_ctx.clearRect(0, 0, w*2, h*2);
  dragnnect2d_ctx.font = "50px Arial";
  dragnnect2d_ctx.fillStyle = colors[dev_id];
  dragnnect2d_ctx.fillText(dev_id, 30, 50);
  dragnnect2d_draw(data);
})

function dragnnect2d_draw(devs) {
    if (dragnnect2d_canvas.getContext) {
      var i = 0;
      devs.forEach(dev => {
        dragnnect2d_ctx.moveTo(dev[0][0]/10 + w, dev[0][1]/10 + h);
        dragnnect2d_ctx.beginPath();
        dev.forEach(pnt => {
          dragnnect2d_ctx.lineTo(pnt[0]/10 + w, pnt[1]/10 + h);
        });
        dragnnect2d_ctx.strokeStyle = colors[i];
        dragnnect2d_ctx.fillStyle = colors[i];
        dragnnect2d_ctx.fill();
        dragnnect2d_ctx.font = "30px Arial";
        dragnnect2d_ctx.fillStyle = '#212121';
        dragnnect2d_ctx.fillText(i, dev[0][0]/10 + w + 10, dev[0][1]/10 + h + 30);
        
        i++;
      });
      
      
      // dragnnect2d_ctx.lineTo(100, 75);
      // dragnnect2d_ctx.lineTo(100, 25);
      
    }
  }