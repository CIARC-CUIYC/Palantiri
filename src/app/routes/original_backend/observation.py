import logging

from flask import Blueprint, jsonify
from src.app.models.melvin import melvin

bp = Blueprint('observation', __name__)

@bp.before_request
def observation_mute_log():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)

@bp.after_request
def observation_unmute_log():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)


@bp.route('/observation', methods=['GET'])
def get_observation():
    return jsonify(melvin.get_observation()), 200
