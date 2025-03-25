from flask import Flask
from src.app.routes import observation, reset, control

def create_app():
    app = Flask(__name__)

    app.register_blueprint(observation.bp)
    app.register_blueprint(reset.bp)
    app.register_blueprint(control.bp)

    return app