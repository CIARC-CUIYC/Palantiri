import math
import random
from datetime import timedelta

import numpy as np
from typing import List, Union, Tuple

from numpy import floating

from src.app.constants import SatStates, TRANSITION_TIME_STANDARD, TRANSITION_TIME_TO_SAFE, \
    TRANSITION_TIME_FROM_SAFE, BEACON_GUESS_TOLERANCE, MAP_WIDTH, MAP_HEIGHT, ACC_CONST


class Helpers:

    @staticmethod
    @staticmethod
    def clamp(n: Union[int, float], minimum: Union[int, float], maximum: Union[int, float]) -> Union[int, float]:
        """
        Clamp a number between a minimum and maximum.

        Args:
            n (Union[int, float]): Value to clamp.
            minimum (Union[int, float]): Lower bound.
            maximum (Union[int, float]): Upper bound.

        Returns:
            Union[int, float]: Clamped value.
        """
        return max(minimum, min(n, maximum))

    @staticmethod
    def get_transition_time(current_state: SatStates, target_state: SatStates) -> int:
        """
        Return time required to transition between two states.

        Args:
            current_state (SatStates): Current state.
            target_state (SatStates): Target state.

        Returns:
            int: Duration of the transition in seconds.
        """
        if current_state == SatStates.SAFE:
            transition_time = TRANSITION_TIME_FROM_SAFE
        elif target_state == SatStates.SAFE:
            transition_time = TRANSITION_TIME_TO_SAFE
        else:
            transition_time = TRANSITION_TIME_STANDARD

        return transition_time

    @staticmethod
    def wrap_coordinate(value: float, max_value: float) -> float:
        """
        Wrap a coordinate value within 0 and max_value.

        Args:
            value (float): Coordinate.
            max_value (float): Max boundary.

        Returns:
            float: Wrapped value.
        """
        return ((value % max_value) + max_value) % max_value

    @staticmethod
    def format_sim_duration(duration: timedelta) -> str:
        """
        Format simulation duration as a time string.

        Args:
            duration (np.timedelta64): Time duration.

        Returns:
            str: Time string in HH:MM:SS format.
        """
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def receive_noisy_measurement(beac_pos: List[float], melvin_pos: List[float]) -> float:
        """
        Simulate receiving a noisy measurement of distance.

        Args:
            beac_pos (List[float]): Beacon position.
            melvin_pos (List[float]): Satellite position.

        Returns:
            float: Noisy measured distance.
        """
        noise_gain: float = random.uniform(-1, 1)

        true_distance_np: floating = np.linalg.norm(np.array(beac_pos) - np.array(melvin_pos))
        true_distance: float = float(true_distance_np)

        noise: float = 3.0 * BEACON_GUESS_TOLERANCE + 0.1 * (true_distance + 1)

        noisy_distance: float = true_distance + noise_gain * noise

        return noisy_distance

    @staticmethod
    def unwrapped_to(object_1: List[float], object2: List[float]) -> float:
        """
        Compute shortest wrapped vector distance.

        Args:
            object_1 (List[float]): From position.
            object2 (List[float]): To position.

        Returns:
            float: Shortest unwrapped distance.
        """
        # Generate all wrapped projections from object1 to object2
        options = Helpers.get_projected_in_range(object_1, object2, [1, 0, -1], [1, 0, -1])

        # Select the one with the smallest squared distance
        best_vector, _ = min(options, key=lambda item: item[1])
        best_vector_sq = math.sqrt(best_vector[0] * best_vector[0] + best_vector[1] * best_vector[1])

        return best_vector_sq

    @staticmethod
    def to(object1: List[float], object2: List[float]) -> List[float]:
        """
        Compute vector from one point to another.

        Args:
            object1 (List[float]): Start position.
            object2 (List[float]): End position.

        Returns:
            List[float]: Vector from object1 to object2.
        """
        return [object2[0] - object1[0], object2[1] - object1[1]]

    @staticmethod
    def get_projected_in_range(object_1: List[float], object_2: List[float], x_range: List[int], y_range: List[int]) -> \
            List[Tuple[List[float], float]]:
        """
                Get all coordinate projections with wrap-around logic.

                Args:
                    object_1 (List[float]): Start position.
                    object_2 (List[float]): End position.
                    x_range (List[int]): X direction offsets.
                    y_range (List[int]): Y direction offsets.

                Returns:
                    List[Tuple[List[float], float]]: Tuples of vector and distance.
                """
        options = []

        for x_sign in x_range:
            for y_sign in y_range:
                target = [object_2[0] + MAP_WIDTH * x_sign, object_2[1] + MAP_HEIGHT * y_sign]

                to_target = Helpers.to(object_1, target)
                to_target_abs_sq = math.sqrt(to_target[0] ** 2 + to_target[1] ** 2)

                options.append((to_target, to_target_abs_sq))

        return options

    @staticmethod
    def is_pos_in_bounds(position: List[int]) -> bool:
        """
        Validate if position is within map boundaries.

        Args:
            position (List[float]): Position to validate.

        Returns:
            bool: True if in bounds.
        """
        return 0 <= position[0] < MAP_WIDTH and 0 <= position[1] < MAP_HEIGHT

    @staticmethod
    def compute_vel_magnitude(v: List[float]) -> float:
        """
        Compute the magnitude of a velocity vector.

        Args:
            v (List[float]): Velocity vector.

        Returns:
            float: Magnitude.
        """
        return math.sqrt(v[0] ** 2 + v[1] ** 2)

    @staticmethod
    def angle_between(v1: List[float], v2: List[float]) -> float:
        """
        Calculate angle (in degrees) between two vectors.

        Args:
            v1 (List[float]): First vector.
            v2 (List[float]): Second vector.

        Returns:
            float: Angle between vectors.
        """
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = Helpers.compute_vel_magnitude(v1)
        mag2 = Helpers.compute_vel_magnitude(v2)
        cos_theta = dot / (mag1 * mag2)
        cos_theta = max(min(cos_theta, 1), -1)  # Clamp for safety
        angle_rad = math.acos(cos_theta)
        return math.degrees(angle_rad)

    @staticmethod
    def compute_acceleration_limits(dvx: float, dvy: float) -> Tuple[float, float]:
        """
        Compute given acceleration limits based on desired delta-V.

        Args:
            dvx (float): Delta velocity in x.
            dvy (float): Delta velocity in y.

        Returns:
            Tuple[float, float]: Acceleration limits in x and y.
        """
        ax = math.sqrt(pow(ACC_CONST, 2) / (1 + (dvy / dvx) ** 2)) if dvx != 0 else 0
        ay = math.sqrt(pow(ACC_CONST, 2) / (1 + (dvx / dvy) ** 2)) if dvy != 0 else 0
        return ax, ay

    @staticmethod
    def validate_velocity_change(old_v: List[float], target_v: List[float]) -> List[Tuple[float, float]]:
        """
        Generate a velocity change plan from current to target velocity.

        Args:
            old_v (List[float]): Current velocity.
            target_v (List[float]): Desired velocity.

        Returns:
            List[Tuple[float, float]]: Sequence of velocity steps.
        """
        plan: List[Tuple[float, float]] = []
        current_v: List[float] = old_v.copy()

        while True:
            dvx = target_v[0] - current_v[0]
            dvy = target_v[1] - current_v[1]

            if abs(dvx) < 1e-3 and abs(dvy) < 1e-3:
                break  # Target reached

            ax_abs, ay_abs = Helpers.compute_acceleration_limits(abs(dvx), abs(dvy))
            ax = math.copysign(ax_abs, dvx)
            ay = math.copysign(ay_abs, dvy)
            ax = min(ax, dvx)
            ay = min(ay, dvy)

            step_vx = current_v[0] + ax
            step_vy = current_v[1] + ay

            current_v = [step_vx, step_vy]
            plan.append((ax, ay))

        return plan
