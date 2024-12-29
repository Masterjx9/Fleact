import os
from flask import Flask
from fleact import Fleact
import dotenv

dotenv.load_dotenv()

if os.environ.get("templatePath"):
    print("Using custom template path:", os.environ.get("templatePath"))
    app = Flask(__name__, template_folder=os.environ.get("templatePath"))
else:
    app = Flask(__name__)
fleact = Fleact(app)
print("Current Working Directory:", os.getcwd())
print("Templates Path Exists:", os.path.exists(os.path.join(os.getcwd(), "templates", "index.html")))

# Ensure routes are imported here to register them
from app import routes
