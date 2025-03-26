from flask import Blueprint, request, jsonify

from src.app.constants import MIN_ALLOWED_VEL, MAX_ALLOWED_VEL, SatStates
from src.app.helpers import Helpers
from src.app.models.melvin import melvin
from werkzeug.exceptions import BadRequest

bp = Blueprint('control', __name__, url_prefix='/control')


@bp.route('/', methods=['PUT'])
def control():
    try:
        data = request.get_json()
        response = {"message": ""}
        status_code = 200

        required_fields = ["vel_x", "vel_y", "camera_angle", "state"]
        if not all(field in data for field in required_fields):
            raise BadRequest("Missing required control fields.")

        if melvin.melvin_state != data["state"]:
            try:
                ControlValidation.validate_input_state(data["state"])
                melvin.update_state(state=data["state"])
                response["message"] += "Target state updated successfully."
            except BadRequest as e:
                response["error"] = str(e)
                status_code = 400

        try:
            ControlValidation.validate_input_angle(data["camera_angle"])
            ControlValidation.validate_input_velocity([data["vel_x"], data["vel_y"]])

            melvin.update_control(
                vel_x=data["vel_x"],
                vel_y=data["vel_y"],
                camera_angle=data["camera_angle"],
            )
            response["message"] += "Control values updated successfully."
        except BadRequest as e:
            response["error"] = str(e)
            status_code = 400

        return jsonify(response), status_code


    except ValueError as e:
        raise BadRequest(f"Invalid value: {e}")


class ControlValidation:

    @staticmethod
    def validate_input_state(input_state):
        if input_state not in melvin.states:
            raise BadRequest("Invalid target state.")

        if melvin.melvin_state == SatStates.TRANSITION:
            raise BadRequest("Target state cannot be set during transition.")

    @staticmethod
    def validate_input_angle(input_angle):
        if input_angle not in melvin.camera_angles:
            raise BadRequest("Invalid camera angle.")

        if melvin.melvin_state != SatStates.ACQUISITION:
            raise BadRequest("Camera angle can only be set during acquisition.")

    @staticmethod
    def validate_input_velocity(input_vel):
        if input_vel[0] < 0 or input_vel[1] < 0:
            raise BadRequest("Velocity must be positive.")

        if MIN_ALLOWED_VEL > Helpers.calculate_absolute_velocity(
                [input_vel[0], input_vel[1]]) or MAX_ALLOWED_VEL < Helpers.calculate_absolute_velocity(
            [input_vel[0], input_vel[1]]):
            raise BadRequest(
                f"Velocity out of bounds. Absolute velocity must be between {MIN_ALLOWED_VEL} and {MAX_ALLOWED_VEL}.")

        if melvin.melvin_state != SatStates.ACQUISITION:
            raise BadRequest("Velocity can only be set during acquisition.")
