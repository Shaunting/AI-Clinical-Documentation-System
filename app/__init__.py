from flask import Flask
from dotenv import load_dotenv
import os


def create_app():
    # Load .env from the project root
    load_dotenv(
        dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    )

    app = Flask(__name__, template_folder="templates", static_folder="static")

    from .routes.web_routes import bp as web_bp
    from .routes.pipeline_routes import bp as pipeline_bp
    from .routes.notes_routes import bp as notes_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(notes_bp)

    return app
