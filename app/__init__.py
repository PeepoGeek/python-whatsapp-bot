from flask import Flask, jsonify
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    # Healthcheck endpoint
    @app.route("/healthcheck", methods=["GET"])
    def healthcheck():
        return jsonify({"status": "ok"}), 200


    return app
