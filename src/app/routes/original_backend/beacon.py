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

    # Fallback to query params if no JSON body
    if not data and request.args:
        _beacon_id = request.args.get("beacon_id", type=int)
        _guess_pos = [
            request.args.get("height", type=int),
            request.args.get("width", type=int)
        ]
        data = {"beacon_id": _beacon_id, "guess": _guess_pos}

    if not data or 'beacon_id' not in data or 'guess' not in data:
        raise BadRequest("Payload must include 'beacon_id' and 'guess' (x, y).")

    beacon_id: Optional[int] = data['beacon_id']
    guess_pos: List[int] = data['guess'][::-1]  # has to be flipped because it's given in [height, width]

    BeaconValidation.validate_input_beacon_position(guess_pos)

    beacon = next((b for b in obj_manager.beacon_list if b.id == beacon_id), None)
    if not beacon:
        return jsonify({"error": "Beacon not found."}), 404

    if beacon_id:
        beacon_guess_tracker.setdefault(beacon_id, 0)
    else:
        return jsonify({"error": "Missing 'beacon_id' in request body."}), 400

    if beacon_guess_tracker[beacon_id] >= 3:
        return jsonify({"error": "Maximum number of guesses reached for this beacon."}), 403

    true_beac_pos: List[float] = [float(beacon.width), float(beacon.height)]
    guess_pos_float: List[float] = [float(guess_pos[0]), float(guess_pos[1])]

    guess_beac_distance: float = Helpers.unwrapped_to(true_beac_pos, guess_pos_float)
    beacon_guess_tracker[beacon_id] += 1

    if guess_beac_distance <= BEACON_GUESS_TOLERANCE:
        obj_manager.obj_list.remove(beacon)
        obj_manager.beacon_list.remove(beacon)
        return jsonify({"status": "success", "attempts_made": beacon_guess_tracker[beacon_id]}), 200
    else:
        return jsonify({"status": "failure", "attempts_made": beacon_guess_tracker[beacon_id]}), 200


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
