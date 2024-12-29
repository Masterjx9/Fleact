<script>
    const ws = new WebSocket("ws://" + window.location.host + "/ws");

    ws.onmessage = function(event) {
        console.log("Received:", event.data);
    };

    function sendMessage(buttonId) {
        const message = { action: "click", id: buttonId };
        ws.send(JSON.stringify(message));
    }
</script>
