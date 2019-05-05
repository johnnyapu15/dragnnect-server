//<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
importScripts("//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js");
var socket;
      
function init() {
    socket.on('update', function(data) {
        postMessage({
            m: "update",
            data:data
        });
    });
    socket.on('connect', function() {
        socket.emit('join');
    });
    socket.on('ntp_0', function() {
        //t1 = Date.now();
        socket.emit('ntp_1', Date.now());
    });

    socket.on('draw', function(data) {
        postMessage({
            m:"drawArranged",
            data:data
        });
    });


    //////////////2d demo ///////////////////////////////////
    // socket.on('demo-init', function(data) {
    //     //demo_init(data);
    //     ctx_2d_demo.width = canvas_2d_demo.width;
    //     ctx_2d_demo.height = canvas_2d_demo.height;
    //     //alert(str(ctx_2d_demo.width) + str(ctx_2d_demo.height));
    // });

    // Listening function
    // socket.on('demo-receive', function(data) {
    //     // data['pnt']: ctx data demonstrated by world-coordinates. (3d)
    //     // Transform the pnt to local-coordinates.
    //     drawDemo(data['pnt']);
    // });

    socket.on('demo-2d-line', function(data) {
        postMessage({
            m:"demo-2d-line",
            data:data
        });
    });

    socket.on('2d-pnt-draw', function(data) {
        postMessage({
            m:"demo-2d-pnt",
            data:data
        });
    });
}



//////////////2d demo end//////////////////////////////////
// socket.on('redirect', function (data) {
//     window.location = data.url;
// });

//socket.on('connect', function() {

//});



// ex: e = {emit: true, m: 'connect', data:'123123'}
onmessage = function(e) {
    var t = e.data['init'];
    if (e.data["emit"]) {
        if (e.data["data"] != undefined) {
            socket.emit(e.data["m"], e.data["data"]);
        }
        else {
            socket.emit(e.data["m"]);
        }
    } else if (e.data["init"]) {
        socket = io.connect(e.data["data"]);
        init();
    }
    // } else {
    //     switch (e.m) {
    //         case 'leave':
    //             socket.emit('leave');
    //             break;
    //         case 'connect':
    //             socket.emit('join', e.data);
    //             break;
    //         case 'ntp_0':
    //             socket.emit('ntp_1', Date.now());
    //             break;
    //         case 'update':
    //             count = e.data.count;
    //             document.getElementById("textarea").innerHTML = "#Room: " + room_id + "\nDev Number: " + count;
    //             break;
    //         case 'reset_lines':
                
    //     };
    // }
};

// function leave() {
//     socket.emit('leave');
//     history.back();
//     };
    
    
    
//     function resetLines() {
//         socket.emit('reset_lines');
//     }
    


