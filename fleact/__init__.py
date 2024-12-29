from threading import Lock
from flask import render_template
from flask_socketio import SocketIO, send, emit
import json
from fleact.registry import find_element_by_fleact_id
class Fleact:
    """
    A Flask extension for adding WebSocket-based reactivity.
    """

    def __init__(self, app=None):
        self.clients = []
        self.lock = Lock()
        self.ws_script = """
        <script src="https://cdn.socket.io/4.8.1/socket.io.min.js" integrity="sha384-mkQ3/7FUtcGyoppY6bz/PORYoGqOl7/aSUMn2ymDOJcapfS6PHqxhRTMh1RR0Q6+" crossorigin="anonymous"></script>
        <script>
            const socket = io.connect("http://" + window.location.host);

            socket.on("connect", () => {
                console.log("Connected to WebSocket");
            });

// Updated socket.on logic
socket.on("message", (data) => {
    console.log("Received message:", data);
    const parsed = typeof data === "string" ? JSON.parse(data) : data; // Check if it's a string before parsing
    console.log("Parsed message:", parsed);
    console.log("Parsed message:", parsed.target);

    const targetElement = document.querySelector(`[fleact-id="${parsed.target}"]`);
    if (!targetElement) {
        console.error("Target element not found for fleact-id:", parsed.target);
        return;
    }

    if (parsed.action === "update-counter") {
        console.log("Updating counter:", parsed.value);
        targetElement.innerText = "Counter: " + parsed.value;
    } else if (parsed.action === "update-content") {
        console.log("Updating content:", parsed.content);
        targetElement.innerText = parsed.content;
    }
});



function sendMessage(message, event) {
    // Ensure the event is valid
    event = event || window.event;

    // Get the element that triggered the event
    const target = event.target || event.srcElement;

    // Log information about the target element
    console.log("Event Target:", target);

    // Optionally include details about the element in the message
    const elementInfo = {
        tag: target.tagName,
        classes: target.className,
        attributes: [...target.attributes].map(attr => ({
            name: attr.name,
            value: attr.value
        })),
        text: target.innerText || target.textContent
    };

    console.log("Element Info:", elementInfo);
    const fleact_id = elementInfo.attributes.find(attr => attr.name === "fleact-id").value;
    socket.send(JSON.stringify({ message, elementInfo, "fleact-id": fleact_id }));
}

        </script>
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
            """
            Initialize the Flask app with WebSocket support.
            """
            self.socketio = SocketIO(app)

            @self.socketio.on("connect")
            def handle_connect():
                print("Client connected")

            @self.socketio.on("disconnect")
            def handle_disconnect():
                print("Client disconnected")

            @self.socketio.on("message")
            def handle_message(data):
                print(f"Message received: {data}")
                data = json.loads(data)
                action = data.get("message")
       
                fleact_id = data.get("fleact-id")  # Use fleact-id for all actions
                if action == "increment":
                    
                    element = find_element_by_fleact_id(fleact_id)  # Implement this method
                    target_fleact_id = element.target
                    print(f"Target Fleact ID: {target_fleact_id}")
                    if element:
                        current_counter = element.get_state("counter", 0)
                        new_counter = current_counter + data.get("amount", 1)
                        element.set_state("counter", new_counter)
                        self.broadcast("update-counter", {"target": target_fleact_id, "value": new_counter})
                elif action == "update-content":
                    content = data.get("content")
                    self.broadcast("update-content", {"fleact-id": fleact_id, "content": content})
                elif action == "toggle-visibility":
                    self.broadcast("toggle-visibility", {"fleact-id": fleact_id})
                elif action == "add-class":
                    class_name = data.get("class_name")
                    self.broadcast("add-class", {"fleact-id": fleact_id, "class_name": class_name})
                elif action == "remove-class":
                    class_name = data.get("class_name")
                    self.broadcast("remove-class", {"fleact-id": fleact_id, "class_name": class_name})
                elif action == "set-attribute":
                    attribute = data.get("attribute")
                    self.broadcast("set-attribute", {"fleact-id": fleact_id, "attribute": attribute})
                elif action == "update-input":
                    value = data.get("value")
                    self.broadcast("update-input", {"fleact-id": fleact_id, "value": value})
                elif action == "custom-event":
                    event = data.get("event")
                    payload = data.get("payload")
                    self.broadcast("custom-event", {"event": event, "payload": payload})
                elif action == "append-child":
                    parent_fleact_id = data.get("parent-fleact-id")
                    content = data.get("content")
                    self.broadcast("append-child", {"parent-fleact-id": parent_fleact_id, "content": content})
                elif action == "remove-child":
                    parent_fleact_id = data.get("parent-fleact-id")
                    child_fleact_id = data.get("child-fleact-id")
                    self.broadcast("remove-child", {"parent-fleact-id": parent_fleact_id, "child-fleact-id": child_fleact_id})
                else:
                    print(f"Unknown action: {action}")


    def render_html_string(self, html_string):
        """
        Injects the WebSocket connection into raw HTML strings.
        """
        # Find the closing </body> or </html> tag and inject the WebSocket script
        if "</body>" in html_string:
            print(html_string.replace("</body>", f"{self.ws_script}</body>"))
            return html_string.replace("</body>", f"{self.ws_script}</body>")
        elif "</html>" in html_string:
            print(html_string.replace("</html>", f"{self.ws_script}</html>"))
            return html_string.replace("</html>", f"{self.ws_script}</html>")
        else:
            # If no tags are found, append the script to the end
            return html_string + self.ws_script

    def render_template_with_ws(self, template_name, **context):
        """
        Renders a Jinja template and injects the WebSocket connection.
        """
        rendered_html = render_template(template_name, **context)
        return self.render_html_string(rendered_html)

    def handle_websocket(self, ws):
        """
        WebSocket handler for managing reactive updates.
        """
        with self.lock:
            self.clients.append(ws)

        while not ws.closed:
            message = ws.receive()
            if message:
                self.broadcast(message)

        with self.lock:
            self.clients.remove(ws)

    def broadcast(self, event, data):
        """
        Broadcast an event with data to all connected clients.
        """
        data["action"] = event
        send(data, broadcast=True)

