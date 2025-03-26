from enum import Enum

MAP_WIDTH = 21600
MAP_HEIGHT = 10800

START_POS_X = 7638
START_POS_Y = 5089
START_POS = [START_POS_X, START_POS_Y]

START_VEL_X = 4.35
START_VEL_Y = 5.49
START_VEL = [START_VEL_X, START_VEL_Y]
MIN_ALLOWED_VEL = 3.0
MAX_ALLOWED_VEL = 71.0
MAX_ALLOWED_VEL_ANGLE = 170

ACC_CONST = 0.04

FUEL_COST = 0.03

START_BAT = 100.0
START_FUEL = 100.0

SIM_STEP_DUR = 0.5

TRANSITION_TIME_STANDARD = 3 * 60
TRANSITION_TIME_FROM_SAFE = 20 * 60
TRANSITION_TIME_TO_SAFE = 1 * 60

BEACON_MAX_DETECT_RANGE = 2000
BEACON_GUESS_TOLERANCE = 75


class SatStates(Enum):
    DEPLOYMENT = "deployment"
    ACQUISITION = "acquisition"
    CHARGE = "charge"
    COMMS = "comms"
    SAFE = "safe"
    TRANSITION = "transition"

    @staticmethod
    def is_valid_sat_state(input_state):
        return input_state in {state.value for state in SatStates}


# TODO: Check correct values
class StateBatteryRate(Enum):
    DEPLOYMENT = -0.025
    ACQUISITION = -0.2
    CHARGE = 0.2
    TRANSITION = 0
    SAFE = 0.05
    COMMS = -0.016


class CameraAngle(Enum):
    NARROW = "narrow"
    NORMAL = "normal"
    WIDE = "wide"

    @staticmethod
    def is_valid_camera_angle(input_angle):
        return input_angle in {angle.value for angle in CameraAngle}

    def get_side_length(self):
        if self == CameraAngle.NARROW:
            return 600
        elif self == CameraAngle.NORMAL:
            return 800
        elif self == CameraAngle.WIDE:
            return 1000
