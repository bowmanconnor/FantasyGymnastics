
    // =============
    // == Globals ==
    // =============
    const dimension = [document.documentElement.clientWidth, document.documentElement.clientHeight];
    var canvas = document.getElementById('canvas');
    var canvasContext = canvas.getContext('2d'); 
    var memCanvas = document.createElement('canvas');
    var memCtx = memCanvas.getContext('2d');

    var started = false;
    var lastx = 0;
    var lasty = 0;
    var points = [];

    const clearButton = document.getElementById('clear-button');
    const imageButton = document.getElementById('image-button');
    const image = document.getElementById("image");
    const penButton = document.getElementById("pen");
    const eraserButton = document.getElementById("eraser");

    const state = {
        mousedown: false
    };

    var mode;
    
    // ===================
    // == Configuration ==
    // ===================
    const lineWidth = 9;
    const fillStyle = 'black';
    const strokeStyle = 'black';

    if (dimension[0] > dimension[1]){
        canvas.width = dimension[1]*.9;
        canvas.height = dimension[1]*.9;
        memCanvas.width = dimension[0]*.9;
        memCanvas.height = dimension[0]*.9;         
        image.width = dimension[1]*.8;
        image.height = dimension[1]*.8;
    } else {
        canvas.width = dimension[0]*.9;
        canvas.height = dimension[0]*.9; 
        memCanvas.width = dimension[0]*.9;
        memCanvas.height = dimension[0]*.9;        
        image.width = dimension[0]*.8;
        image.height = dimension[0]*.8;        
    }

    canvasContext.lineWidth = 9;
    canvasContext.lineJoin = 'round';
    canvasContext.lineCap = 'round';


    penMode();
    
    // =====================
    // == Event Listeners ==
    // =====================
    canvas.addEventListener('mousedown', handleWritingStart);
    canvas.addEventListener('mousemove', handleWritingInProgress);
    canvas.addEventListener('mouseup', handleDrawingEnd);
    canvas.addEventListener('mouseout', handleDrawingEnd);

    canvas.addEventListener('touchstart', handleWritingStart);
    canvas.addEventListener('touchmove', handleWritingInProgress);
    canvas.addEventListener('touchend', handleDrawingEnd);

    clearButton.addEventListener('click', handleClearButtonClick);
    imageButton.addEventListener('click', handleToImageButtonClick);

    penButton.addEventListener('click', handlePenModeButtonClick);
    eraserButton.addEventListener('click', handleEraserModeButtonClick);


    // ====================
    // == Event Handlers ==
    // ====================
    function handleWritingStart(e) {
        e.preventDefault();
        var m = getMouse(e, canvas);
        points.push({
            x: m.x,
            y: m.y
        });
        started = true;

    }

    function handleWritingInProgress(e) {
        e.preventDefault();
        if (started) {
            var m = getMouse(e, canvas);
            if (mode=="pen"){
                canvasContext.globalCompositeOperation="source-over";
                memCtx.globalCompositeOperation="source-over";
                canvasContext.clearRect(0, 0, 300, 300);
                // put back the saved content
                canvasContext.drawImage(memCanvas, 0, 0);
                points.push({
                    x: m.x,
                    y: m.y
                });
                drawPoints(canvasContext, points);
            } else {
                canvasContext.globalCompositeOperation="destination-out";
                memCtx.globalCompositeOperation="destination-out";
                canvasContext.clearRect(0, 0, 300, 300);
                // put back the saved content
                canvasContext.drawImage(memCanvas, 0, 0);
                points.push({
                    x: m.x,
                    y: m.y
                });
                drawPoints(canvasContext, points);
            }

        }
    }

    function handleDrawingEnd(e) {
        e.preventDefault();
        if (started) {
            started = false;
            // When the pen is done, save the resulting context
            // to the in-memory canvas
            memCtx.clearRect(0, 0, 300, 300);
            memCtx.drawImage(canvas, 0, 0);
            points = [];
        }
    }

    function handleClearButtonClick(e) {
        e.preventDefault();

        clearCanvas();
    }

    function handleToImageButtonClick(e) {
        e.preventDefault();

        toImage();
    }

    function handlePenModeButtonClick(e) {
        e.preventDefault();

        penMode();
    }

    function handleEraserModeButtonClick(e) {
        e.preventDefault();

        eraserMode();
    }
    // ======================
    // == Helper Functions ==
    // ======================
    function getMousePositionOnCanvas(e) {
        const clientX = e.clientX || e.touches[0].clientX;
        const clientY = e.clientY || e.touches[0].clientY;
        const { offsetLeft, offsetTop } = e.target;
        const canvasX = clientX - offsetLeft;
        const canvasY = clientY - offsetTop;

        return { x: canvasX, y: canvasY };
    }

    function clearCanvas() {
        canvasContext.clearRect(0, 0, canvas.width, canvas.height);
    }

    function toImage() {
        image.src = canvas.toDataURL();
        // Canvas2Image.saveAsPNG(canvas);
    }

    function penMode() {
        mode = "pen";
        penButton.style.color = "black";
        eraserButton.style.color = "gray";
    }

    function eraserMode() {
        mode = "eraser";
        penButton.style.color = "gray";
        eraserButton.style.color = "black";
    }

    function drawPoints(canvasContext, points) {
        // draw a basic circle instead
        if (points.length < 6) {
            var b = points[0];
            canvasContext.beginPath(), canvasContext.arc(b.x, b.y, canvasContext.lineWidth / 2, 0, Math.PI * 2, !0), canvasContext.closePath(), canvasContext.fill();
            return
        }
        canvasContext.beginPath(), canvasContext.moveTo(points[0].x, points[0].y);
        // draw a bunch of quadratics, using the average of two points as the control point
        for (i = 1; i < points.length - 2; i++) {
            var c = (points[i].x + points[i + 1].x) / 2,
                d = (points[i].y + points[i + 1].y) / 2;
            canvasContext.quadraticCurveTo(points[i].x, points[i].y, c, d)
        }
        canvasContext.quadraticCurveTo(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y), canvasContext.stroke()
    }

    function getMouse(e, canvas) {
        var element = canvas, offsetX = 0, offsetY = 0, mx, my;
      
        // Compute the total offset. It's possible to cache this if you want
        if (element.offsetParent !== undefined) {
          do {
            offsetX += element.offsetLeft;
            offsetY += element.offsetTop;
          } while ((element = element.offsetParent));
        }
      
        mx = e.pageX - offsetX;
        my = e.pageY - offsetY;
      
        // We return a simple javascript object with x and y defined
        return {x: mx, y: my};
      }
