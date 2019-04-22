var canvas_2d_demo = document.getElementById('canvas-2d-demo');

var ctx_2d_demo = canvas_2d_demo.getContext('2d');

ctx_2d_demo.lineWidth = 30;
ctx_2d_demo.lineJoin = 'round';
ctx_2d_demo.lineCap = 'round';
ctx_2d_demo.strokeStyle = '#5A6068';

// Init
function demo_init(data) {
    ctx_2d_demo.alpha = data[1];
    // Inversed rotation
    ctx_2d_demo.theta = -1 * data[2];
    // data[2, 3]: Origin point of this device on world-coordinates.
    // local x, y: Scaled origin point on world-coordinates.
    ctx_2d_demo.local_x = data[0][0][0] / ctx_2d_demo.alpha;
    ctx_2d_demo.local_y = data[0][0][1] / ctx_2d_demo.alpha;

};
socket.on('demo-init', function(data) {
    //demo_init(data);
    ctx_2d_demo.width = canvas_2d_demo.getBoundingClientRect().width;
    ctx_2d_demo.height = canvas_2d_demo.getBoundingClientRect().height;
});

// Listening function
socket.on('demo-receive', function(data) {
    // data['pnt']: ctx data demonstrated by world-coordinates. (3d)
    // Transform the pnt to local-coordinates.
    drawDemo(data['pnt']);
});

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

function drawDemo(pnt) {
    var tr = transfromToLocal2d(pnt);
    ctx_2d_demo.width = canvas_2d_demo.getBoundingClientRect().width;
    ctx_2d_demo.height = canvas_2d_demo.getBoundingClientRect().height;
    console.log(tr);
    //log point text
    document.getElementById('a-2d-demo').innerText = "pnt: (" + tr[0].toString() + ", " + tr[1].toString() + ")";
    document.getElementById('a-2d-demo').innerText += ctx_2d_demo.width.toString() + " " + ctx_2d_demo.height.toString();
    if ((0 < tr[0] && tr[0] < ctx_2d_demo.width) &&
        (0 < tr[1] && tr[1] < ctx_2d_demo.height)) {
            //draw a point
            ctx_2d_demo.clearRect(0, 0, ctx_2d_demo.width*2, ctx_2d_demo.height*2);

            ctx_2d_demo.moveTo(tr[0], tr[1]);
            ctx_2d_demo.stroke();
        }
}