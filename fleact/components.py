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
        self.state = {}  # Store reactive variables

        # Ensure the element has a unique fleact-id
        self.props["fleact-id"] = self.fleact_id
        
        register_component(self)

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
        # Replace 'class_name' with 'class' in props
        attributes = " ".join(
            f'{("class" if key == "class_name" else key)}="{value}"' for key, value in self.props.items()
        )
        return f"<{self.tag} {attributes}>{self.content}</{self.tag}>"
