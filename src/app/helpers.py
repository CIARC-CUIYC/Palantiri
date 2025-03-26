import math
import random
import numpy as np
from typing import List
from src.app.constants import SatStates, StateBatteryRate, TRANSITION_TIME_STANDARD, TRANSITION_TIME_TO_SAFE, \
    TRANSITION_TIME_FROM_SAFE, BEACON_GUESS_TOLERANCE, MAP_WIDTH, MAP_HEIGHT


class Helpers:

    @staticmethod
    def get_charge_per_sec_enum(state):
        if isinstance(state, StateBatteryRate):
            return state.value
        else:
            raise RuntimeError(f"Unknown State: {state}")

    @staticmethod
    def clamp(n, minimum, maximum):
        if n < minimum:
            return minimum
        elif n > maximum:
            return maximum
        else:
            return n

    @staticmethod
    def get_charge_per_sec(state):
        # Map SatStates to StateBatteryRate
        state_to_battery_rate = {
            SatStates.DEPLOYMENT: StateBatteryRate.DEPLOYMENT,
            SatStates.ACQUISITION: StateBatteryRate.ACQUISITION,
            SatStates.CHARGE: StateBatteryRate.CHARGE,
            SatStates.TRANSITION: StateBatteryRate.TRANSITION,
            SatStates.SAFE: StateBatteryRate.SAFE,
            SatStates.COMMS: StateBatteryRate.COMMS,
        }

        if state in state_to_battery_rate:
            # Get corresponding StateBatteryRate Enum
            battery_rate_enum = state_to_battery_rate[state]
            # Retrieve the charge per second value using the provided method
            return Helpers.get_charge_per_sec_enum(battery_rate_enum)
        else:
            raise RuntimeError(f"Unknown State: {state}")

    @staticmethod
    def get_transition_time(current_state, target_state):
        if current_state == SatStates.SAFE:
            transition_time = TRANSITION_TIME_FROM_SAFE
        elif target_state == SatStates.CHARGE:
            transition_time = 2 * TRANSITION_TIME_STANDARD
        elif target_state == SatStates.SAFE:
            transition_time = TRANSITION_TIME_TO_SAFE
        else:
            transition_time = TRANSITION_TIME_STANDARD

        return transition_time

    @staticmethod
    def wrap_coordinate(value, max_value):
        return ((value % max_value) + max_value) % max_value

    # TODO: Move to API call. Think about illegal state changes
    @staticmethod
    def validate_mode_change(current_state, target_state):
        if current_state == SatStates.TRANSITION:
            return False
        if target_state == SatStates.DEPLOYMENT:
            return False
        return True

    @staticmethod
    def format_sim_duration(duration):
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def receive_noisy_measurement(beac_pos, melvin_pos):
        noise_gain = random.uniform(-1, 1)
        true_distance = np.linalg.norm(np.array(beac_pos) - np.array(melvin_pos))
        noise = 3 * BEACON_GUESS_TOLERANCE + 0.1 * (true_distance + 1)

        noisy_distance = true_distance + noise_gain * noise

        return noisy_distance

    @staticmethod
    def euclidean_distance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    @staticmethod
    def unwrapped_to(object_1, object2):
        # Generate all wrapped projections from object1 to object2
        options = Helpers.get_projected_in_range(object_1, object2, [1, 0, -1], [1, 0, -1])

        # Select the one with the smallest squared distance
        best_vector, _ = min(options, key=lambda item: item[1])
        best_vector_sq = math.sqrt(best_vector[0] * best_vector[0] + best_vector[1] * best_vector[1])

        return best_vector_sq

    @staticmethod
    def to(object1, object2):
        distance_vec = [object2[0] - object1[0], object2[1] - object1[1]]
        return distance_vec

    @staticmethod
    def get_projected_in_range(object_1, object_2, x_range: List[int], y_range: List[int]):
        options = []

        for x_sign in x_range:
            for y_sign in y_range:
                target = [object_2[0] + MAP_WIDTH * x_sign, object_2[1] + MAP_HEIGHT * y_sign]

                to_target = Helpers.to(object_1, target)
                to_target_abs_sq = math.sqrt(to_target[0] ** 2 + to_target[1] ** 2)

                options.append((to_target, to_target_abs_sq))

        return options

    @staticmethod
    def calculate_absolute_velocity(velocity):
        return math.sqrt(velocity[0] ** 2 + velocity[1] ** 2)

    @staticmethod
    def is_pos_in_bounds(position):
        return 0 <= position[0] < MAP_WIDTH and 0 <= position[1] < MAP_HEIGHT
