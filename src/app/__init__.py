from flask import Flask
from src.app.routes.helper_backend import palantiri
from src.app.routes.original_backend import control, objective, observation, reset, announcements, beacon, get_image, \
    daily_map


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    This function initializes the Flask app and registers all the required blueprints
    for routing different parts of the application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app: Flask = Flask(__name__)

    app.register_blueprint(observation.bp)
    app.register_blueprint(reset.bp)
    app.register_blueprint(control.bp)
    app.register_blueprint(palantiri.bp)
    app.register_blueprint(beacon.bp)
    app.register_blueprint(announcements.bp)
    app.register_blueprint(get_image.bp)
    app.register_blueprint(daily_map.bp)
    app.register_blueprint(objective.bp)

    return app
