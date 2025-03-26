from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from src.app.constants import BEACON_GUESS_TOLERANCE
from src.app.helpers import Helpers
from src.app.models.obj_manager import obj_manager

bp = Blueprint('beacon', __name__, url_prefix='/beacon')

# Store guess counts
beacon_guess_tracker = {}  # beacon_id -> int


@bp.route('/', methods=['PUT'])
def guess_beacon():
    data = request.get_json(silent=True) or {}

    # Fallback to query params if no JSON body
    if not data and request.args:
        beacon_id = request.args.get("beacon_id", type=int)
        guess_pos = [
            request.args.get("height", type=int),
            request.args.get("width", type=int)
        ]
        data = {"beacon_id": beacon_id, "guess": guess_pos}

    if not data or 'beacon_id' not in data or 'guess' not in data:
        raise BadRequest("Payload must include 'beacon_id' and 'guess' (x, y).")

    beacon_id = data['beacon_id']
    guess_pos = data['guess'][::-1]  # has to be flipped because its given in [height, width]

    beacon = next((b for b in obj_manager.beacon_list if b.id == beacon_id), None)
    if not beacon:
        return jsonify({"error": "Beacon not found."}), 404

    beacon_guess_tracker.setdefault(beacon_id, 0)

    if beacon_guess_tracker[beacon_id] >= 3:
        return jsonify({"error": "Maximum number of guesses reached for this beacon."}), 403

    true_beac_pos = [beacon.width, beacon.height]

    distance = Helpers.unwrapped_to(true_beac_pos, guess_pos)
    beacon_guess_tracker[beacon_id] += 1

    if distance <= BEACON_GUESS_TOLERANCE:
        obj_manager.obj_list.remove(beacon)
        obj_manager.beacon_list.remove(beacon)
        return jsonify({"result": "success", "distance": distance, "guesses_used": beacon_guess_tracker[beacon_id]})
    else:
        return jsonify({"result": "failure", "distance": distance, "guesses_used": beacon_guess_tracker[beacon_id]})
