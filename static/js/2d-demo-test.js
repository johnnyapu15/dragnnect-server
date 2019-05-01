var canvas_2d_demo = document.getElementById('canvas-2d-demo');
var div_2d_demo = document.getElementById('div-2d-demo');
canvas_2d_demo.width = div_2d_demo.clientWidth;
canvas_2d_demo.height = div_2d_demo.clientHeight;
var ctx_2d_demo = canvas_2d_demo.getContext('2d');

ctx_2d_demo.lineWidth = 1;
ctx_2d_demo.lineJoin = 'round';
ctx_2d_demo.lineCap = 'round';
ctx_2d_demo.strokeStyle = '#5A6068';
ctx_2d_demo.save();

var img_coord = [0, 0];
var img_delta = [0, 0];
var img_anim = [0, 0];
var an_f = 0.4;
var anim = false;
var update = false;
// Init
function demo_init(data) {
    ctx_2d_demo.alpha = data[1];
    // Inversed rotation
    ctx_2d_demo.theta = -1 * data[2];
    // data[2, 3]: Origin point of this device on world-coordinates.
    // local x, y: Scaled origin point on world-coordinates.
    ctx_2d_demo.local_x = data[0][0][0];
    ctx_2d_demo.local_y = data[0][0][1];
    

};
socket.on('demo-init', function(data) {
    //demo_init(data);
    ctx_2d_demo.width = canvas_2d_demo.width;
    ctx_2d_demo.height = canvas_2d_demo.height;
    //alert(str(ctx_2d_demo.width) + str(ctx_2d_demo.height));
});

// Listening function
socket.on('demo-receive', function(data) {
    // data['pnt']: ctx data demonstrated by world-coordinates. (3d)
    // Transform the pnt to local-coordinates.
    drawDemo(data['pnt']);
});
var lineData;
socket.on('demo-2d-line', function(data) {
    lineData = data;
    canvas_2d_demo.width = div_2d_demo.clientWidth;
    canvas_2d_demo.height = div_2d_demo.clientHeight;
    ctx_2d_demo.width = canvas_2d_demo.width;
    ctx_2d_demo.height = canvas_2d_demo.height;
    //console.log((ctx_2d_demo.width).toString() + (ctx_2d_demo.height).toString());

    // ctx_2d_demo.clearRect(ctx_2d_demo.local_x - 100, ctx_2d_demo.local_y - 100,
    //     ctx_2d_demo.local_x + ctx_2d_demo.width + 100, ctx_2d_demo.local_y + ctx_2d_demo.height + 100);
    line_draw(data);
    draw([0, 0]);
    img_coord = [0,0];
});
function line_draw(data) {
    ctx_2d_demo.restore();
    ctx_2d_demo.clearRect(0, 0, ctx_2d_demo.width, ctx_2d_demo.height);
    ctx_2d_demo.save();
    translateMap();

    data['lines'].forEach(l => {
        ctx_2d_demo.beginPath();
        ctx_2d_demo.moveTo(0, 0);
        ctx_2d_demo.lineTo(l[0], l[1]);
        ctx_2d_demo.stroke();
    });
}
socket.on('2d-pnt-draw', function(data) {

   line_draw(lineData);
    anim = data.v; //true
   img_delta[0] = data.x;
   img_delta[1] = data.y;
   update = true;
});
window.requestAnimationFrame(draw);
// Rotate point with local origin. Return array(x, y).
function rotatePnt(angle, pnt_x, pnt_y) {
    var x = Math.cos(angle) * pnt_x - Math.sin(angle) * pnt_y;
    var y = Math.sin(angle) * pnt_x + Math.cos(angle) * pnt_y;
    return [x, y];
}
function transfromToLocal2d(pnt) {
    //pnt: 3d world-coord points array, y is height.
    // rotation
    var ret = rotatePnt(ctx_2d_demo.theta, pnt[0], pnt[2]);
    // shift
    ret[0] -= ctx_2d_demo.local_x;
    ret[1] -= ctx_2d_demo.local_y;
    // scale
    ret[0] /= ctx_2d_demo.alpha;
    ret[1] /= ctx_2d_demo.alpha;

    //rotation (WIth local origin)
    return ret
}

function translateMap() {
    ctx_2d_demo.rotate(ctx_2d_demo.theta);
    ctx_2d_demo.scale(1 / ctx_2d_demo.alpha, 1 / ctx_2d_demo.alpha);
    ctx_2d_demo.translate(-ctx_2d_demo.local_x, -ctx_2d_demo.local_y);
};
var tr = [0, 0];
function drawDemo(pnt) {
    //var tr = transfromToLocal2d(pnt);
    tr = [pnt[0], pnt[2]];
    ctx_2d_demo.width = canvas_2d_demo.getBoundingClientRect().width;
    ctx_2d_demo.height = canvas_2d_demo.getBoundingClientRect().height;
    translateMap();
    console.log(tr);
    
    //log point text
    document.getElementById('a-2d-demo').innerText = "pnt: (" + tr[0].toString() + ", " + tr[1].toString() + ")";
    document.getElementById('a-2d-demo').innerText += ctx_2d_demo.width.toString() + " " + ctx_2d_demo.height.toString();
    if ((0 < tr[0] && tr[0] < ctx_2d_demo.width) &&
        (0 < tr[1] && tr[1] < ctx_2d_demo.height)) {
            //draw a point
            ctx_2d_demo.clearRect(0, 0, ctx_2d_demo.width, ctx_2d_demo.height);
            ctx_2d_demo.moveTo(tr[0], tr[1]);
            ctx_2d_demo.fillRect(tr[0], tr[1], tr[0] + 10, tr[1] + 50);
        }
};

var gkhead = new Image;
gkhead.src = 'http://phrogz.net/tmp/gkhead.jpg';
function draw() {
    if (update) {
        if (anim) {
            img_delta[0] /= 2;
            img_delta[1] /= 2;
            if (img_delta[0] < 2)
                update = false;
        }
        else {
            
            update = false;
        }
        img_coord[0] -= img_delta[0];
        img_coord[1] -= img_delta[1];
        img_anim[0] = an_f * img_anim[0] + (1 - an_f) * img_coord[0];
        img_anim[1] = an_f * img_anim[1] + (1 - an_f) * img_coord[1];

    }
    console.log("drawing..." + img_coord[0] + ", " + img_coord[1]);
    ctx_2d_demo.drawImage(gkhead, img_anim[0], img_anim[1]);
    window.requestAnimationFrame(draw);
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect(); 
    return { x: evt.clientX - rect.left, y: evt.clientY - rect.top }; 
};

function writeMessage(_canvas, _message) {
    var context = _canvas.getContext('2d'); 
    context.clearRect(0, 0, _canvas.width, _canvas.height); 
    context.font = '18pt Calibri'; 
    context.fillStyle = 'black'; 
    context.fillText(_message, 10, 25); 
};

var dragStart = false;
var startPos;
canvas_2d_demo.addEventListener('mousedown', function(evt) {
    dragStart = true;
    startPos = getMousePos(canvas_2d_demo, evt);
}, false);
canvas_2d_demo.addEventListener('mousemove', function(evt) {
    if (dragStart) {
        var mousePos = getMousePos(canvas_2d_demo, evt); 
        var delta = {x: startPos.x - mousePos.x, y: startPos.y - mousePos.y, v:false};
        var message = 'Mouse position: ' + mousePos.x + ',' + mousePos.y;
        //console.log("Delta: " + delta.x + ', ' + delta.y);
        socket.emit('2d-demo-pnt', delta);
        //document.getElementById('a-2d-demo').innerText = message + "\npnt: (" + tr[0].toString() + ", " + tr[1].toString() + ")";
        document.getElementById('a-2d-demo').innerText = message + "\n" + ctx_2d_demo.local_x.toString() + " " + ctx_2d_demo.local_y.toString();
        //writeMessage(canvas, message); 
        startPos = mousePos;
    }
}, false);
canvas_2d_demo.addEventListener('mouseup', function(evt) {
    dragStart = false;
    var delta = {x: 0, y:0, v: true};
    socket.emit('2d-demo-pnt', delta);
});

canvas_2d_demo.addEventListener('touchstart', function(evt) {
    evt.preventDefault();
    startPos = {x: evt.changedTouches[0].pageX, y:evt.changedTouches[0].pageY};
    dragStart = true;
}, false);
canvas_2d_demo.addEventListener('touchmove', function(evt) {
    if (dragStart) {
        var mousePos = {x: evt.changedTouches[0].pageX, y:evt.changedTouches[0].pageY}; 
        var delta = {x: startPos.x - mousePos.x, y: startPos.y - mousePos.y, v:false};
        var message = 'Touch position: ' + mousePos.x + ',' + mousePos.y;
        //console.log("Delta: " + delta.x + ', ' + delta.y);
        socket.emit('2d-demo-pnt', delta);
        //document.getElementById('a-2d-demo').innerText = message + "\npnt: (" + tr[0].toString() + ", " + tr[1].toString() + ")";
        document.getElementById('a-2d-demo').innerText = message + "\n" + ctx_2d_demo.local_x.toString() + " " + ctx_2d_demo.local_y.toString();
        //writeMessage(canvas, message); 
        startPos = mousePos;
    }
}, false);
canvas_2d_demo.addEventListener('touchend', function(evt) {
    dragStart = false;
    var delta = {x: 0, y:0, v: true};
    socket.emit('2d-demo-pnt', delta);
}, false);