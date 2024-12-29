from threading import Lock
from flask import render_template
from flask_socketio import SocketIO, send, emit
import json
from fleact.registry import find_element_by_fleact_id
from fleact.ws_script import ws_script
class Fleact:
    """
    A Flask extension for adding WebSocket-based reactivity.
    """

    def __init__(self, app=None):
        self.clients = []
        self.lock = Lock()
        self.ws_script = ws_script
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
                element = find_element_by_fleact_id(fleact_id)  # Implement this method
       
                if action == "increment":
                    target_fleact_id = element.target
                    print(f"Target Fleact ID: {target_fleact_id}")
                    current_counter = element.get_state("counter", 0)
                    new_counter = current_counter + data.get("amount", 1)
                    element.set_state("counter", new_counter)
                    self.broadcast("update-counter", {"target": target_fleact_id, "value": new_counter})
                elif action == "trigger-callback":
                    callback_name = data.get("callback_name")
                    if callback_name in element.callbacks:
                        callback_config = element.callbacks[callback_name]
                        callback_function = callback_config.get("call")
                        if callable(callback_function):
                            # Execute the callback function
                            print(f"Executing callback: {callback_name}")
                            callback_result = callback_function()

                            if isinstance(callback_result, dict):  # Ensure structured response
                                print(f"Callback result: {callback_result}")
                                if "reactiveActions" in callback_result:
                                    actions = callback_result["reactiveActions"]
                                    if isinstance(actions, list):
                                        for action in actions:
                                            if action["action"] == "if-else":
                                                element.set_if_else(action["value"])
                                                if "targetValue" in action:
                                                    target_element = find_element_by_fleact_id(element.callbacks[data["callback_name"]]["target"])
                                                    target_element.set_if_else(action["targetValue"])
                                                self.broadcast("if-else", action)
                                            elif action["action"] == "update-content":
                                                element.set_state("content", action["content"])
                                                self.broadcast("state-updated", action)
                                                if "targetContent" in action:
                                                    target_element = find_element_by_fleact_id(element.callbacks[data["callback_name"]]["target"])
                                                    target_element.set_state("content", action["targetContent"])
                                                    self.broadcast("state-updated", action)
                                                
                                    else:
                                        print(f"Invalid reactiveActions format: {actions}")
                                else:
                                    self.broadcast("state-updated", callback_result)
                            else:
                                print(f"Invalid callback result format: {callback_result}")

                elif action == "update-state":
                    state = data.get("state")
                    element.state.update(state)
                    self.broadcast("state-updated", state)
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
                    
            @self.socketio.on("get-if-else")
            def handle_get_if_else(data):
                fleact_id = data.get("fleact-id")
                if not fleact_id:
                    print("fleact-id not provided")
                    return {"error": "fleact-id not provided"}

                # Find the element by fleact-id
                element = find_element_by_fleact_id(fleact_id)
                if not element:
                    print(f"Element with fleact-id {fleact_id} not found")
                    return {"error": f"Element with fleact-id {fleact_id} not found"}

                return {"if_else": element.if_else}


    def render_html_string(self, html_string):
        """
        Injects the WebSocket connection into raw HTML strings.
        """
        # Find the closing </body> or </html> tag and inject the WebSocket script
        if "</body>" in html_string:
            return html_string.replace("</body>", f"{self.ws_script}</body>")
        elif "</html>" in html_string:
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
        emit(event, data)

