from enum import Enum

# Map dimensions (pixels)
MAP_WIDTH: int = 21600
MAP_HEIGHT: int = 10800

# Initial satellite position
START_POS_X: float = 7638.0
START_POS_Y: float = 5089.0
START_POS: list[float] = [START_POS_X, START_POS_Y]

# Initial satellite velocity
START_VEL_X: float = 4.35
START_VEL_Y: float = 5.49
START_VEL: list[float] = [START_VEL_X, START_VEL_Y]

# Velocity constraints
MIN_ALLOWED_VEL: float = 3.0
MAX_ALLOWED_VEL: float = 71.0
MAX_ALLOWED_VEL_ANGLE: int = 170

# Acceleration constant (units per sim step)
ACC_CONST: float = 0.01

# burn constants (battery/fuel) (unit per sim step)
FUEL_COST: float = 0.015
ADD_BAT_COST_BURN: float = -0.025

# Starting resources
START_BAT: float = 100.0
START_FUEL: float = 100.0

# Sim step duration (seconds)
SIM_STEP_DUR: float = 0.5

# Transition times between satellite states (seconds)
TRANSITION_TIME_STANDARD: int = (3 * 60) - 1
TRANSITION_TIME_FROM_SAFE: int = 20 * 60
TRANSITION_TIME_TO_SAFE: int = 1 * 60

# Beacon detection settings
BEACON_MAX_DETECT_RANGE: int = 2000
BEACON_GUESS_TOLERANCE: int = 75


class SatStates(Enum):
    """
    Enum representing the different operational states of the satellite.
    """
    DEPLOYMENT = "deployment"
    ACQUISITION = "acquisition"
    CHARGE = "charge"
    COMMS = "comms"
    SAFE = "safe"
    TRANSITION = "transition"

    @staticmethod
    def is_valid_sat_state(input_state: str) -> bool:
        """
        Checks if a string corresponds to a valid satellite state.

        Args:
            input_state (str): The state to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return input_state in {state.value for state in SatStates}


class StateBatteryRate(Enum):
    """
    Enum mapping each satellite state to its associated battery consumption or charge rate.
    Positive values indicate charging, negative indicate consumption.
    """
    DEPLOYMENT = -0.025
    ACQUISITION = -0.05
    CHARGE = 0.05
    TRANSITION = 0
    SAFE = 0.0125
    COMMS = -0.004


class CameraAngle(Enum):
    """
    Enum representing different camera field-of-view settings.
    """
    NARROW = "narrow"
    NORMAL = "normal"
    WIDE = "wide"

    @staticmethod
    def is_valid_camera_angle(input_angle: str) -> bool:
        """
        Check if a string corresponds to a valid camera angle.

        Args:
            input_angle (str): The angle to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        return input_angle in {angle.value for angle in CameraAngle}

    def get_side_length(self) -> int:
        """
        Get the image side length (in pixels) associated with the camera angle.

        Returns:
            int: Side length in pixels.
        """
        if self == CameraAngle.NARROW:
            return 600
        elif self == CameraAngle.NORMAL:
            return 800
        elif self == CameraAngle.WIDE:
            return 1000

        return 0
