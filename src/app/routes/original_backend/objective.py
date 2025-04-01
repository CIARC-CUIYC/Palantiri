import logging

from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import BadRequest

from src.app.models.obj_manager import obj_manager

bp = Blueprint('objective', __name__)


@bp.route('/objective', methods=['GET'])
def objective() -> Response:
    """
    Retrieve all active objectives (zoned and beacon).

    Returns:
        JSON: A dictionary containing lists of objectives.
    """
    return jsonify(obj_manager.get_all_objectives())


@bp.route('/objective', methods=['PUT'])
def add_objectives() -> tuple[Response, int]:
    """
    Add new objectives via JSON body. Supports manual and random generation.

    Expected JSON structure:
    {
        "num_random_zoned": int,
        "num_random_beacon": int,
        "zoned_objectives": [ ... ],
        "beacon_objectives": [ ... ]
    }

    Returns:
        Tuple[JSON, int]: Response with created objectives, or error.
    """
    data = request.get_json()
    if not data:
        raise BadRequest("Missing request body.")

    responses = {
        "zoned_objectives": [],
        "beacon_objectives": []
    }

    # --- Manual Zoned Objectives ---
    manual_zoned = data.get("zoned_objectives", [])
    for raw_obj in manual_zoned:
        try:
            new_obj = obj_manager.create_zoned_from_dict(raw_obj)
            responses["zoned_objectives"].append(new_obj.to_dict())
        except Exception as e:
            raise BadRequest(f"Failed to add zoned objective: {e}")

    # --- Manual Beacon Objectives ---
    manual_beacons = data.get("beacon_objectives", [])
    for raw_obj in manual_beacons:
        try:
            new_obj = obj_manager.create_beacon_from_dict(raw_obj)
            responses["beacon_objectives"].append(new_obj.to_dict())
        except Exception as e:
            raise BadRequest(f"Failed to add beacon objective: {e}")

    # --- Randomly Generated Objectives ---
    num_rand_zoned = data.get("num_random_zoned", 0)
    num_rand_beacon = data.get("num_random_beacon", 0)

    new_zo_objs = obj_manager.create_random_zoned_objective(num_rand_zoned)
    new_bo_objs = obj_manager.create_random_beacon_objective(num_rand_beacon)

    for new_zo in new_zo_objs:
        responses["zoned_objectives"].append(new_zo.info_to_endpoint())
    for new_bo in new_bo_objs:
        responses["beacon_objectives"].append(new_bo.info_to_endpoint())

    if not responses["zoned_objectives"] and not responses["beacon_objectives"]:
        raise BadRequest("No objectives submitted or requested.")

    return jsonify(responses), 201


@bp.route('/', methods=['DELETE'])
def delete_objective() -> tuple[Response, int]:
    """
    Delete an objective by ID, using a query parameter.

    Query Parameters:
        id (int): The objective ID to delete.

    Returns:
        JSON: Confirmation or error message.
    """
    obj_id = request.args.get('id', type=int)

    if obj_id is None:
        raise BadRequest("Missing 'id' query parameter.")

    success = obj_manager.delete_objective_by_id(obj_id)

    if success:
        return jsonify({"message": f"Objective with ID {obj_id} deleted."}), 200
    else:
        return jsonify({"message": f"Objective with ID {obj_id} not found."}), 404
