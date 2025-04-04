from typing import Dict, Any, Optional, List, Tuple

from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import BadRequest

from src.app.constants import BEACON_GUESS_TOLERANCE, MAP_HEIGHT, MAP_WIDTH
from src.app.helpers import Helpers
from src.app.models.obj_manager import obj_manager

bp = Blueprint('beacon', __name__)

# Store guess counts: beacon_id, num_guesses
beacon_guess_tracker: dict[int, int] = {}


@bp.route('/beacon', methods=['PUT'])
def guess_beacon() -> Tuple[Response, int]:
    """
    Handle a beacon position guess. Accepts either JSON or query parameters.

    Request:
        JSON or query string with:
        - beacon_id (int)
        - guess (List[int] or height + width query params)

    Returns:
        JSON response with success/failure status and attempt count.
    """
    data: Dict[str, Any] = request.get_json(silent=True) or {}

    # Fallback to query params
    if not data and request.args:
        _beacon_id = request.args.get("beacon_id", type=int)
        _guess_pos = [
            request.args.get("height", type=int),
            request.args.get("width", type=int)
        ]
        data = {"beacon_id": _beacon_id, "guess": _guess_pos}

    if not data or "beacon_id" not in data or "guess" not in data:
        raise BadRequest("Payload must include 'beacon_id' and 'guess' (x, y).")

    beacon_id: Optional[int] = data["beacon_id"]
    guess_pos: List[int] = data["guess"][::-1]

    if beacon_id is None or not isinstance(beacon_id, int):
        raise BadRequest("'beacon_id' must be a valid integer.")

    BeaconValidation.validate_input_beacon_position(guess_pos)

    beacon = next((b for b in obj_manager.beacon_list if b.id == beacon_id), None)

    if not beacon:
        return jsonify({
            "status": "Could not find beacon.",
            "attempts_made": 0
        }), 404

    beacon_guess_tracker.setdefault(beacon_id, 0)

    # Too many attempts already
    if beacon_guess_tracker[beacon_id] >= 3:
        return jsonify({
            "status": "The beacon could not be found.",
            "attempts_made": beacon_guess_tracker[beacon_id]
        }), 200

    true_pos = [float(beacon.width), float(beacon.height)]
    guess_pos_float = [float(guess_pos[0]), float(guess_pos[1])]
    distance = Helpers.unwrapped_to(true_pos, guess_pos_float)

    # Successful guess
    if distance <= BEACON_GUESS_TOLERANCE:
        obj_manager.obj_list.remove(beacon)
        obj_manager.beacon_list.remove(beacon)
        beacon_guess_tracker[beacon_id] += 1
        return jsonify({
            "status": "The beacon was found!",
            "attempts_made": beacon_guess_tracker[beacon_id]
        }), 200

    # Failed guess
    beacon_guess_tracker[beacon_id] += 1

    # Failed last guess
    if beacon_guess_tracker[beacon_id] == 3:
        return jsonify({
            "status": "No more rescue attempts. The beacon has not be found.",
            "attempts_made": beacon_guess_tracker[beacon_id]
        }), 200

    return jsonify({
        "status": "The beacon could not be found.",
        "attempts_made": beacon_guess_tracker[beacon_id]
    }), 200


class BeaconValidation:
    """
    Helper class to validate beacon guess input.
    """

    @staticmethod
    def validate_input_beacon_position(input_guess_beacon_pos: List[int]) -> None:
        """
        Validate guess position shape and boundaries.

        Args:
            input_guess_beacon_pos (List[int]): [x, y] guess coordinates.

        Raises:
            BadRequest: If guess is invalid or out of bounds.
        """
        if len(input_guess_beacon_pos) != 2:
            raise BadRequest("Guess must hold an x and y coordinate.")

        if Helpers.is_pos_in_bounds(input_guess_beacon_pos) is False:
            raise BadRequest(
                f"Guess must be within the bounds of the beacon. X bounds: [0, {MAP_WIDTH}], Y bounds: [0, {MAP_HEIGHT}].")
