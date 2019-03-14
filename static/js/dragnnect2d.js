function draw(pnts) {
    var canvas = document.getElementById('canvas');
    if (canvas.getContext) {
      var ctx = canvas.getContext('2d');
  
      ctx.beginPath();
      ctx.moveTo(pnts[0]);
      pnts.forEach(element => {
        ctx.lineTo(element);
      });
      ctx.lineTo(100, 75);
      ctx.lineTo(100, 25);
      ctx.fill();
    }
  }