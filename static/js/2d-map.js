
var map;
var send;
var start;
var pre;
var pntSelf;
var marker;
var uploadValue = false;
var loaded = false;
var clicked = false;
function initMap() {
  start = new google.maps.LatLng(37.5838657, 127.0587771);
  pre = start;
  map = new google.maps.Map(document.getElementById('div-2d-demo'), {
    center: start,
    zoom: 15,
    disableDefaultUI: true
  });
  
  marker = new google.maps.Marker({
    position: start,
    map: map,
    title: 'Click to zoom'
  });
  if (map != undefined) loaded = true;
  map.addListener('dragstart', function() {
    clicked = true;
  })
  map.addListener('idle', function () {
    if (clicked) {
      cen = map.getCenter();
      send = cen
      console.log(send);
      uploadValue = true;
      pre = cen;
      clicked = false;
    }
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
        //p = fromLatLngToPixel(send);
        var s = getModified(send, pntSelf)
        sendPnt([s.lat(), s.lng()]);
        uploadValue = false;
    }
};
window.setInterval(sync, 50);


function pntUpdate(pnt) {
    p = new google.maps.LatLng(
        pnt[0], pnt[1]);
    // p.x += pntSelf.x;
    // p.y += pntSelf.y;
    // l = fromPixelToLatLng(p);
    l = getUpdated(p, pntSelf);
    //update = true;
    map.panTo(l);
};

function demo_init(data) {
    // Inversed rotation
    document.getElementById('div-2d-demo').style.transform = 'rotate(' + String(-1 * data[2]) + 'rad)';
    // data[2, 3]: Origin point of this device on world-coordinates.
    // local x, y: Scaled origin point on world-coordinates.
    
    pntSelf = new google.maps.Point(data[0][0][0], data[0][0][1]);
    //map.panTo(fromPixelToLatLng(pntSelf));
    start = getModified(start, pntSelf);
    map.panTo(start);
    
};

function getModified(_start, _pntSelf) {
  //console.log(_pntSelf);
  
  var o = fromLatLngToPixel(_start);
  var ret = new google.maps.Point(o.x - _pntSelf.x, o.y - _pntSelf.y);
  return fromPixelToLatLng(ret);
}
function getUpdated(_start, _pntSelf) {
  //console.log(_pntSelf);
  
  var o = fromLatLngToPixel(_start);
  var ret = new google.maps.Point(o.x + _pntSelf.x, o.y + _pntSelf.y);
  return fromPixelToLatLng(ret);
}