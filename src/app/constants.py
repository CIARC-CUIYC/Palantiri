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


class SatStates(Enum):
    DEPLOYMENT = "deployment"
    ACQUISITION = "acquisition"
    CHARGE = "charge"
    COMMS = "comms"
    SAFE = "safe"


class CameraAngle(Enum):
    NARROW = "narrow"
    NORMAL = "normal"
    WIDE = "wide"
