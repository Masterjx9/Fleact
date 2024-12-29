from app import app  # Import the app instance
from fleact import Fleact  # Import the Fleact class
from fleact.components import ReactiveElement  # Import the reactive button class

# Create an instance of Fleact (if not already created in app/__init__.py)
fleact = Fleact(app)

@app.route("/")
def home():
    pElement = ReactiveElement(
        tag="p",
        content="Counter: 0",
        id="counter-value"
    )
    button = ReactiveElement(
        tag="button",
        content="Click Me!",
        id="submit-button",
        class_name="btn-primary",
        onclick="sendMessage('increment')",
        target=pElement.props["fleact-id"]
    )
    pElement.set_state("counter", 0)

    raw_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reactive Flask</title>
    </head>
    <body>
        <h1>Reactive Counter</h1>
        {pElement.render()}
        {button.render()}
    </body>
    </html>
    """
    return fleact.render_html_string(raw_html)

@app.route("/templatetest")
def template_test():
    pElement = ReactiveElement(
        tag="p",
        content="Counter: 0",
        id="counter-value"
    )
    button = ReactiveElement(
        tag="button",
        content="Click Me!",
        id="submit-button",
        class_name="btn-primary",
        onclick="sendMessage('increment')",
        target=pElement.props["fleact-id"]
    )
    pElement.set_state("counter", 0)
    
    return fleact.render_template_with_ws(
    "index.html",
    pElement=pElement.render(),  
    button=button.render()
)