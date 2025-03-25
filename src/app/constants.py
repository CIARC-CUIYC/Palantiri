from enum import Enum

START_POS_X = 7638
START_POS_Y = 5089
START_POS = [START_POS_X, START_POS_Y]

START_VEL_X = 4.35
START_VEL_Y = 5.49
START_VEL = [START_VEL_X, START_VEL_Y]

START_BAT = 100.0
START_FUEL = 100.0

SIM_STEP_DUR = 0.5

TRANSITION_TIME_STANDARD = 3 * 60
TRANSITION_TIME_FROM_SAFE = 20 * 60
TRANSITION_TIME_TO_SAFE = 1 * 60


class SatStates(Enum):
    DEPLOYMENT = "deployment"
    ACQUISITION = "acquisition"
    CHARGE = "charge"
    COMMS = "comms"
    SAFE = "safe"
    TRANSITION = "transition"


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
