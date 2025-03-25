from src.app.constants import SatStates, StateBatteryRate, TRANSITION_TIME_STANDARD, TRANSITION_TIME_TO_SAFE, \
    TRANSITION_TIME_FROM_SAFE


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
        if target_state == SatStates.CHARGE:
            transition_time = 2 * TRANSITION_TIME_STANDARD
        elif target_state == SatStates.SAFE:
            transition_time = TRANSITION_TIME_TO_SAFE
        else:
            transition_time = TRANSITION_TIME_STANDARD

        return transition_time
