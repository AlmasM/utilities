"""
Main Flask application factory.
Registers all API blueprints and configures the app.
"""

import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

    # Register blueprints — add new api/ modules here
    from api.convert import convert_bp
    from api.health import health_bp

    app.register_blueprint(convert_bp)
    app.register_blueprint(health_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=8080)
