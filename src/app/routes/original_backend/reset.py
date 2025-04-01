from typing import Tuple

from flask import Blueprint, jsonify
from src.app.models.melvin import melvin

bp = Blueprint('reset', __name__)

@bp.route('/reset', methods=['GET'])
def reset() -> Tuple[object, int]:
    """
    Reset the satellite simulation (Melvin) to its initial state.

    Returns:
        Tuple[object, int]: JSON confirmation and HTTP 200 status code.
    """
    melvin.reset()
    return jsonify("Reset the engine successfully."), 200