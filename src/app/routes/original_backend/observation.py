from typing import Tuple

from flask import Blueprint, jsonify, Response
from src.app.models.melvin import melvin

bp = Blueprint('observation', __name__)

@bp.route('/observation', methods=['GET'])
def get_observation() -> Tuple[Response, int]:
    return jsonify(melvin.get_observation()), 200
