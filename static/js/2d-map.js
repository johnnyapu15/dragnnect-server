
var map;
var send;
var pre;
var pntSelf;
var marker;
var uploadValue = false;
function initMap() {
  start = new google.maps.LatLng(-34.397,150.644);
  map = new google.maps.Map(document.getElementById('div-2d-demo'), {
    center: start,
    zoom: 12
  });
  marker = new google.maps.Marker({
    position: start,
    map: map,
    title: 'Click to zoom'
  });
  map.addListener('idle', function () {
    send = map.getCenter() - pre;
    uploadValue = true;
    pre = map.getCenter();
  })
//   marker.addListener('click', function() {
//     map.setZoom(12);
//     map.setCenter(marker.getPosition());
//   });
//   map.addListener('center_changed', function() {
//     // 3 seconds after the center of the map has changed, pan back to the
//     // marker.
//     window.setTimeout(function() {
//       //map.panTo(marker.getPosition());
//       l = fromLatLngToPixel(start);
//     console.log(l);
//     p = fromPixelToLatLng(l);
//     console.log(p.lat());
//     console.log(p.lng());
    
    
//     }, 3000);
//   });
  
}

function fromLatLngToPixel(position) {
    var scale = Math.pow(2, map.getZoom());
    var proj = map.getProjection();
    var bounds = map.getBounds();

    var nw = proj.fromLatLngToPoint(
    new google.maps.LatLng(
    bounds.getNorthEast().lat(),
    bounds.getSouthWest().lng()
    ));
    var point = proj.fromLatLngToPoint(position);

    return new google.maps.Point(
    Math.floor((point.x - nw.x) * scale),
    Math.floor((point.y - nw.y) * scale));
}

function fromPixelToLatLng(pixel) {
    var scale = Math.pow(2, map.getZoom());
    var proj = map.getProjection();
    var bounds = map.getBounds();

    var nw = proj.fromLatLngToPoint(
        new google.maps.LatLng(
            bounds.getNorthEast().lat(),
            bounds.getSouthWest().lng()
    ));
    var point = new google.maps.Point();

    point.x = pixel.x / scale + nw.x;
    point.y = pixel.y / scale + nw.y;

    return proj.fromPointToLatLng(point);
}

function sync() {
    if (uploadValue){
        p = fromLatLngToPixel(send);
        
        sendPnt([p.x - pntSelf.x, p.y - pntSelf.y]);
        uploadValue = false;
    }
};
window.setInterval(sync, 50);


function pntUpdate(pnt) {
    sp = 
    p = new google.maps.LatLng(
        pnt[0], pnt[1]);
    p.x += pntSelf.x;
    p.y += pntSelf.y;
    l = fromPixelToLatLng(p);
    update = true;
    map.panTo(l);
};

function demo_init(data) {
    // Inversed rotation
    document.getElementById('div-2d-demo').style.transform = 'rotate(' + String(-1 * data[2]) + 'deg)';
    // data[2, 3]: Origin point of this device on world-coordinates.
    // local x, y: Scaled origin point on world-coordinates.
    pntSelf = new google.maps.Point(data[0][0][0], data[0][0][1]);
    map.panTo(fromPixelToLatLng(pntSelf));

};