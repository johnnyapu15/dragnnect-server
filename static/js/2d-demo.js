
    // 캔버스 전체 초기화: init(size)
    // 각 디바이스 위치 조정: arrange(position, angle)
    // 드래그로 이미지 이동: moveImg()
    
    // 월드 좌표계와 로컬 좌표계 개념을 나눠서, 서버에서 전송한 월드 좌표계를
    // 디바이스에 최적화된 로컬 좌표계로 변형하여 표현한다.
    // 이 과정에서 필요한 것은 디바이스의 위치와 각도.
    // 이미지의 좌표가 50, 50이고 디바이스의 위치가 20, 40이라면 로컬 좌표는 30, 10이 될 것이다.
    // 배율(scaling)에 대한 것은 고려하지 않아도 되는가?
    
    //var canvas = document.getElementsByTagName('canvas')[0];
    var canvas_2d_demo = document.getElementById('canvas-2d-demo');

	var gkhead = new Image;
    gkhead.src = 'http://phrogz.net/tmp/gkhead.jpg';
    // Adds ctx.getTransform() - returns an SVGMatrix
	// Adds ctx.transformedPoint(x,y) - returns an SVGPoint	
    
    var ctx_2d_demo = canvas_2d_demo.getContext('2d');
    trackTransforms(ctx_2d_demo);
		  
    function redraw(){

        // Clear the entire canvas
        var p1 = ctx_2d_demo.transformedPoint(0,0);
        var p2 = ctx_2d_demo.transformedPoint(canvas_2d_demo.width,canvas_2d_demo.height);
        ctx_2d_demo.clearRect(p1.x,p1.y,p2.x-p1.x,p2.y-p1.y);

        ctx_2d_demo.save();
        ctx_2d_demo.setTransform(1,0,0,1,0,0);
        ctx_2d_demo.clearRect(0,0,canvas_2d_demo.width,canvas_2d_demo.height);
        ctx_2d_demo.restore();

        ctx_2d_demo.drawImage(gkhead,0,0);

    }
        redraw();

      var lastX=canvas_2d_demo.width/2, lastY=canvas_2d_demo.height/2;

      var dragStart,dragged;

      canvas_2d_demo.addEventListener('mousedown',function(evt){
          document.body.style.mozUserSelect = document.body.style.webkitUserSelect = document.body.style.userSelect = 'none';
          lastX = evt.offsetX || (evt.pageX - canvas_2d_demo.offsetLeft);
          lastY = evt.offsetY || (evt.pageY - canvas_2d_demo.offsetTop);
          dragStart = ctx_2d_demo.transformedPoint(lastX,lastY);
          dragged = false;
      },false);

      canvas_2d_demo.addEventListener('mousemove',function(evt){
          lastX = evt.offsetX || (evt.pageX - canvas_2d_demo.offsetLeft);
          lastY = evt.offsetY || (evt.pageY - canvas_2d_demo.offsetTop);
          dragged = true;
          if (dragStart){
            var pt = ctx_2d_demo.transformedPoint(lastX,lastY);
            ctx_2d_demo.translate(pt.x-dragStart.x,pt.y-dragStart.y);
            redraw();
                }
      },false);

      canvas_2d_demo.addEventListener('mouseup',function(evt){
          dragStart = null;
          if (!dragged) zoom(evt.shiftKey ? -1 : 1 );
      },false);

      var scaleFactor = 1.1;

      var zoom = function(clicks){
          var pt = ctx_2d_demo.transformedPoint(lastX,lastY);
          ctx_2d_demo.translate(pt.x,pt.y);
          var factor = Math.pow(scaleFactor,clicks);
          ctx_2d_demo.scale(factor,factor);
          ctx_2d_demo.translate(-pt.x,-pt.y);
          redraw();
      }

      var handleScroll = function(evt){
          var delta = evt.wheelDelta ? evt.wheelDelta/40 : evt.detail ? -evt.detail : 0;
          if (delta) zoom(delta);
          return evt.preventDefault() && false;
      };
    
      canvas_2d_demo.addEventListener('DOMMouseScroll',handleScroll,false);
      canvas_2d_demo.addEventListener('mousewheel',handleScroll,false);


	

	function trackTransforms(ctx){
      var svg = document.createElementNS("http://www.w3.org/2000/svg",'svg');
      var xform = svg.createSVGMatrix();
      ctx.getTransform = function(){ return xform; };

      var savedTransforms = [];
      var save = ctx.save;
      ctx.save = function(){
          savedTransforms.push(xform.translate(0,0));
          return save.call(ctx);
      };
    
      var restore = ctx.restore;
      ctx.restore = function(){
        xform = savedTransforms.pop();
        return restore.call(ctx);
		      };

      var scale = ctx.scale;
      ctx.scale = function(sx,sy){
        xform = xform.scaleNonUniform(sx,sy);
        return scale.call(ctx,sx,sy);
		      };
    
      var rotate = ctx.rotate;
      ctx.rotate = function(radians){
          xform = xform.rotate(radians*180/Math.PI);
          return rotate.call(ctx,radians);
      };
    
      var translate = ctx.translate;
      ctx.translate = function(dx,dy){
          xform = xform.translate(dx,dy);
          return translate.call(ctx,dx,dy);
      };
    
      var transform = ctx.transform;
      ctx.transform = function(a,b,c,d,e,f){
          var m2 = svg.createSVGMatrix();
          m2.a=a; m2.b=b; m2.c=c; m2.d=d; m2.e=e; m2.f=f;
          xform = xform.multiply(m2);
          return transform.call(ctx,a,b,c,d,e,f);
      };
    
      var setTransform = ctx.setTransform;
      ctx.setTransform = function(a,b,c,d,e,f){
          xform.a = a;
          xform.b = b;
          xform.c = c;
          xform.d = d;
          xform.e = e;
          xform.f = f;
          return setTransform.call(ctx,a,b,c,d,e,f);
      };
    
      var pt  = svg.createSVGPoint();
      ctx.transformedPoint = function(x,y){
          pt.x=x; pt.y=y;
          return pt.matrixTransform(xform.inverse());
      }
	}