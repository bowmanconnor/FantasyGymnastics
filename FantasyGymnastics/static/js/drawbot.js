
    // =============
    // == Globals ==
    // =============

    var URL = "send";

    const dimension = [document.documentElement.clientWidth, document.documentElement.clientHeight];
    const canvas = document.getElementById('canvas');
    const canvasContext = canvas.getContext('2d');
    const clearButton = document.getElementById('clear-button');
    const imageButton = document.getElementById('image-button');
    const image = document.getElementById("image");
    const penButton = document.getElementById("pen");
    const eraserButton = document.getElementById("eraser");
    const sendButton = document.getElementById("send");

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
        image.width = dimension[1]*.8;
        image.height = dimension[1]*.8;
    } else {
        canvas.width = dimension[0]*.9;
        canvas.height = dimension[0]*.9;        
        image.width = dimension[0]*.8;
        image.height = dimension[0]*.8;        
    }

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
    sendButton.addEventListener('click', handleSendModeButtonClick);


    // ====================
    // == Event Handlers ==
    // ====================
    function handleWritingStart(event) {
        event.preventDefault();

        const mousePos = getMousePositionOnCanvas(event);

        canvasContext.beginPath();

        canvasContext.moveTo(mousePos.x, mousePos.y);

        canvasContext.lineWidth = lineWidth;
        canvasContext.strokeStyle = strokeStyle;
 
        canvasContext.fill();

        state.mousedown = true;

    }

    function handleWritingInProgress(event) {
        event.preventDefault();

        if (state.mousedown) {
            const mousePos = getMousePositionOnCanvas(event);
            if(mode=="pen"){
                canvasContext.globalCompositeOperation="source-over";
                canvasContext.lineTo(mousePos.x, mousePos.y);
                canvasContext.stroke();
            } else {
                canvasContext.globalCompositeOperation="destination-out";
                canvasContext.lineTo(mousePos.x, mousePos.y);
                canvasContext.stroke();
            }
        }
    }

    function handleDrawingEnd(event) {
        event.preventDefault();

        if (state.mousedown) {

            canvasContext.stroke();
        }

        state.mousedown = false;
    }

    function handleClearButtonClick(event) {
        event.preventDefault();

        clearCanvas();
    }

    function handleToImageButtonClick(event) {
        event.preventDefault();

        toImage();
    }

    function handlePenModeButtonClick(event) {
        event.preventDefault();

        penMode();
    }

    function handleEraserModeButtonClick(event) {
        event.preventDefault();

        eraserMode();
    }

    function handleSendModeButtonClick(event) {
        event.preventDefault();

        sendImage();
    }
    // ======================
    // == Helper Functions ==
    // ======================
    function getMousePositionOnCanvas(event) {
        const clientX = event.clientX || event.touches[0].clientX;
        const clientY = event.clientY || event.touches[0].clientY;
        const { offsetLeft, offsetTop } = event.target;
        const canvasX = clientX - offsetLeft;
        const canvasY = clientY - offsetTop;

        return { x: canvasX, y: canvasY };
    }

    function clearCanvas() {
        canvasContext.clearRect(0, 0, canvas.width, canvas.height);
    }

    function toImage() {
        image.src = canvas.toDataURL();
    }
    
    function sendImage() {
        // Canvas2Image.saveAsPNG(canvas);
        var CSRToken = $('input[name=csrfmiddlewaretoken]').val();
        var image_data = image.src;

        var data = { 
            image: image_data,
            csrfmiddlewaretoken: CSRToken
        }

        $.post(URL, data ,function(response){
                if(response === 'success'){
                     alert('Image saved');
                     location.href="/drawbot";
            }
                else{ alert('Error! :('); }
            });
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

