from flask import Blueprint, jsonify
from src.app.models.melvin import melvin

bp = Blueprint('observation', __name__)


@bp.route('/observation', methods=['GET'])
def get_observation():
    return jsonify(melvin.get_observation()), 200
