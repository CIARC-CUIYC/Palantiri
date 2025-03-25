from flask import Blueprint, request, jsonify
from src.app.models.melvin import melvin
from werkzeug.exceptions import BadRequest

bp = Blueprint('control', __name__, url_prefix='/control')

@bp.route('/', methods=['PUT'])
def control():
    try:
        data = request.get_json()

        required_fields = ["vel_x", "vel_y", "camera_angle", "state"]
        if not all(field in data for field in required_fields):
            raise BadRequest("Missing required control fields.")

        melvin.update_control(
            vel_x=data["vel_x"],
            vel_y=data["vel_y"],
            camera_angle=data["camera_angle"],
            state=data["state"]
        )

        return jsonify({"message": "Control values updated successfully."})

    except ValueError as e:
        raise BadRequest(f"Invalid value: {e}")