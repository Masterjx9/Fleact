import json
from flask import Flask, render_template, request
from flask_sockets import Sockets
from threading import Lock
import uuid
from fleact.registry import register_component

class ReactiveComponent:
    """
    A blueprint for creating reusable reactive components.
    """

    def __init__(self, html_template):
        self.html_template = html_template
        self.fleact_id = f"fleact-{uuid.uuid4().hex}"  # Generate a unique ID for each component

    def render(self, **context):
        """
        Renders the HTML for this component with the given context.
        """
        with open(self.html_template, 'r') as file:
            html = file.read()
        return html.format(**context)

class ReactiveElement(ReactiveComponent):
    """
    A flexible reactive element that can render any HTML tag with customizable attributes and behaviors.
    """

    def __init__(self, tag="div", content="", target=None, **props):
        """
        Initialize the reactive element.

        :param tag: The HTML tag for the element (e.g., 'button', 'div').
        :param content: The inner content of the element (e.g., 'Click Me!').
        :param props: Optional properties for the element (e.g., id, class_name, onclick, listen).
        """
        super().__init__(None)  # No external template needed
        self.tag = tag
        self.content = content
        self.target = target
        self.props = props
        self.callbacks = {}
        self.if_else = None
        self.state = {}  # Store reactive variables

        # Ensure the element has a unique fleact-id
        self.props["fleact-id"] = self.fleact_id
        
        register_component(self)
    def set_if_else(self, condition):
            """
            Sets the if_else property for conditional rendering.
            """
            if isinstance(condition, bool):
                self.if_else = condition
            else:
                raise ValueError("if_else must be a boolean value.")

    def set_state(self, key, value):
        """Set a reactive state variable."""
        self.state[key] = value

    def get_state(self, key, default=None):
        """Get a reactive state variable."""
        return self.state.get(key, default)

    def render(self):
        """
        Renders the HTML for the element with the specified tag and properties.
        """

        callbacks_metadata = {
            name: {"on_load": config.get("on_load", False)} for name, config in self.callbacks.items()
        }
        self.props["fleact-callbacks"] = json.dumps(callbacks_metadata).replace('"', "&quot;")

        attributes_list = []
        for key, value in self.props.items():
            if key == "class_name":
                attributes_list.append(f'class="{value}"')
            elif key == "callbacks":
                continue
            elif key == "props":
                for prop_key, prop_value in value.items():
                    attributes_list.append(f'{prop_key}="{prop_value}"')
            else:
                attributes_list.append(f'{key}="{value}"')
                
            if self.if_else is not None:
                attributes_list.append(f'fleact-if="{self.if_else}"')
                attributes_list.append('style="display: none;"')
                
        attributes = " ".join(attributes_list)
        return f"<{self.tag} {attributes}>{self.content}</{self.tag}>"
    
    def get_on_load_callbacks(self):
        """Retrieve all callbacks marked as on_load=True."""
        return {name: config["call"] for name, config in self.callbacks.items() if config.get("on_load", False)}
