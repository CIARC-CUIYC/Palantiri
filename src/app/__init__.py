from flask import Flask
from src.app.routes.helper_backend import palantiri
from src.app.routes.original_backend import control, objective, observation, reset, announcements, beacon


def create_app():
    app = Flask(__name__)

    app.register_blueprint(observation.bp)
    app.register_blueprint(reset.bp)
    app.register_blueprint(control.bp)
    app.register_blueprint(palantiri.bp)
    app.register_blueprint(objective.bp)
    app.register_blueprint(beacon.bp)
    app.register_blueprint(announcements.bp)

    return app
