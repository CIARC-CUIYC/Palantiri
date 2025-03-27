import logging

from flask import Blueprint, request, jsonify

from src.app.constants import MIN_ALLOWED_VEL, MAX_ALLOWED_VEL, SatStates, CameraAngle, MAX_ALLOWED_VEL_ANGLE
from src.app.helpers import Helpers
from src.app.models.melvin import melvin
from werkzeug.exceptions import BadRequest

bp = Blueprint('control', __name__)


@bp.route('/control', methods=['PUT'])
def control():
    try:
        data = request.get_json()
        response = {}
        status_code = 200

        required_fields = ["vel_x", "vel_y", "camera_angle", "state"]
        if not all(field in data for field in required_fields):
            raise BadRequest("Missing required control fields.")

        safe_mode_block = (melvin.melvin_state is SatStates.SAFE and melvin.bat < 10.0)

        if melvin.melvin_state.value != data["state"] and melvin.state_target is not SatStates.TRANSITION and not safe_mode_block:
            try:
                ControlValidation.validate_input_state(data["state"])
                melvin.update_state(state=data["state"])
                response["status"] = "Target state updated successfully."
            except BadRequest as e:
                response["error"] = str(e)
                status_code = 400

        try:
            ControlValidation.validate_input_angle(data["camera_angle"])
            ControlValidation.validate_input_velocity([data["vel_x"], data["vel_y"]])
            assert(type(data["vel_x"]) == float and type(data["vel_y"]) == float)
            if melvin.melvin_state == SatStates.ACQUISITION:
                melvin.update_control(
                    vel_x=data["vel_x"],
                    vel_y=data["vel_y"],
                    camera_angle=data["camera_angle"],
                )
            else:
                logger = logging.getLogger(__name__)
                logger.warning("Cant change velocity and angle when not in acquisition")

            response["status"] = "Control values updated successfully."
            response["vel_x"] = melvin.vel[0]
            response["vel_y"] = melvin.vel[1]
            response["camera_angle"] = melvin.camera_angle.value
            response["state"] = melvin.melvin_state.value
        except BadRequest as e:
            response["error"] = str(e)
            status_code = 400

        return jsonify(response), status_code


    except ValueError as e:
        raise BadRequest(f"Invalid value: {e}")


class ControlValidation:

    @staticmethod
    def validate_input_state(input_state):
        if not SatStates.is_valid_sat_state(input_state):
            raise BadRequest("Invalid target state")

        if melvin.melvin_state == SatStates.TRANSITION:
            raise BadRequest("Target state cannot be set during transition.")

        if input_state == SatStates.DEPLOYMENT:
            raise BadRequest("Target state cannot be set to DEPLOYMENT.")

        if input_state == SatStates.TRANSITION:
            raise BadRequest("Target state cannot be set to TRANSITION.")

    @staticmethod
    def validate_input_angle(input_angle):
        if not CameraAngle.is_valid_camera_angle(input_angle):
            raise BadRequest("Invalid camera angle.")

    @staticmethod
    def validate_input_velocity(input_vel):
        if input_vel[0] == melvin.vel[0] and input_vel[1] == melvin.vel[1]:
            return

        angle = Helpers.angle_between(melvin.vel, input_vel)
        if angle >= MAX_ALLOWED_VEL_ANGLE:
            raise BadRequest(
                f"Velocity out of bounds. Angle between new and old velocity must be less than {MAX_ALLOWED_VEL_ANGLE} degrees.")

        if MIN_ALLOWED_VEL > Helpers.compute_vel_magnitude(
                [input_vel[0], input_vel[1]]) or MAX_ALLOWED_VEL < Helpers.compute_vel_magnitude(
            [input_vel[0], input_vel[1]]):
            raise BadRequest(
                f"Velocity out of bounds. Absolute velocity must be between {MIN_ALLOWED_VEL} and {MAX_ALLOWED_VEL}.")
