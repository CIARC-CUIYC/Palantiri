from flask import Blueprint, jsonify, Response, make_response
from src.app.models.melvin import melvin

bp = Blueprint('reset', __name__)


@bp.route('/reset', methods=['GET'])
def reset() -> tuple[Response, int]:
    """
    Reset the satellite simulation (Melvin) to its initial state.

    Returns:
        Response: JSON confirmation and HTTP 200 status code.
    """
    melvin.reset()
    return make_response( jsonify("Reset the engine successfully.")), 200
