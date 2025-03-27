import time
import logging
import threading
from collections import OrderedDict
from datetime import timedelta, datetime, timezone

from src.app.constants import *
from src.app.helpers import Helpers

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class Melvin:
    SIM_DUR_PRINTS = 300

    def __init__(self):
        self.pos = START_POS.copy()
        self.vel = START_VEL.copy()
        self.bat = START_BAT
        self.fuel = START_FUEL
        self.melvin_state = SatStates.DEPLOYMENT
        self.camera_angle = CameraAngle.NORMAL

        self.state_target = None
        self.transition_time = None

        self.vel_plan = None

        self.logger = logging.getLogger(self.__class__.__name__)
        self.sim_duration = timedelta(seconds=0)

        self.logger.info("Melvin initialized. Default start values set.")

    def next_sim_step(self):
        self.check_for_transition()
        self.update_pos()
        self.update_battery()

        if self.transition_time:
            self.handle_transition_time()

        if self.vel_plan:
            self.update_velocity()
            self.fuel -= FUEL_COST

        self.sim_duration += timedelta(seconds=SIM_STEP_DUR)

        if self.sim_duration.total_seconds() % self.SIM_DUR_PRINTS == 0:
            self.logger.info(f"Simulation duration: {Helpers.format_sim_duration(self.sim_duration)}")

    def update_pos(self):
        self.pos[0] += self.vel[0] * SIM_STEP_DUR
        self.pos[1] += self.vel[1] * SIM_STEP_DUR

        self.pos[0] = Helpers.wrap_coordinate(self.pos[0], MAP_WIDTH)
        self.pos[1] = Helpers.wrap_coordinate(self.pos[1], MAP_HEIGHT)

    def update_battery(self):
        if self.vel_plan:
            self.bat += ADD_BAT_COST
        self.bat += SIM_STEP_DUR * Helpers.get_charge_per_sec(self.melvin_state)
        self.bat = Helpers.clamp(self.bat, 0, 100)
        if self.bat <= 0 and self.state_target != SatStates.SAFE:
            self.state_target = SatStates.SAFE
            self.logger.info("Melvin battery empty. Forced transition to safe mode.")

    def handle_transition_time(self):
        self.transition_time = max(0, self.transition_time - SIM_STEP_DUR)

        if self.transition_time == 0:
            self.transition_time = None
            self.melvin_state = self.state_target
            self.state_target = None
            self.logger.info(f"Melvin state changed to {self.melvin_state.name}")

    def check_for_transition(self):
        if self.melvin_state != self.state_target and self.state_target is not None and self.melvin_state != SatStates.TRANSITION:
            self.melvin_state = SatStates.TRANSITION
            self.vel_plan = []
            self.transition_time = Helpers.get_transition_time(self.melvin_state, self.state_target)
            self.logger.info(
                f"Melvin state changed to {self.melvin_state.name}. Next state is {self.state_target.name} in {self.transition_time}s.")

    def get_observation(self):
        return OrderedDict({
            "state": self.melvin_state.value,
            "angle": self.camera_angle.value,
            "simulation_speed": 1,
            "width_x": int(round(self.pos[0])),
            "height_y": int(round(self.pos[1])),
            "vx": round(self.vel[0], 2),
            "vy": round(self.vel[1], 2),
            "battery": round(self.bat, 2),
            "max_battery": 100.0,
            "fuel": round(self.fuel, 2),
            "distance_covered": 1.0,
            "area_covered": {"narrow": 0.0, "normal": 0.0, "wide": 0.0},
            "data_volume": {"data_volume_sent": 0, "data_volume_received": 0},
            "images_taken": 0,
            "active_time": 0.0,
            "objectives_done": 0,
            "objectives_points": 0,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        })

    def reset(self):
        self.pos = START_POS.copy()
        self.vel = START_VEL.copy()
        self.bat = START_BAT
        self.fuel = START_FUEL
        self.melvin_state = SatStates.DEPLOYMENT
        self.camera_angle = CameraAngle.NORMAL
        self.logger.info("Melvin reset.")

    def update_state(self, state):
        if self.melvin_state != SatStates.TRANSITION:
            self.state_target = SatStates(state)
            self.logger.info(f"Melvin target state changed to {state}")

    # TODO: Remove unnecessary double checks
    def update_control(self, vel_x, vel_y, camera_angle):
        if self.melvin_state == SatStates.ACQUISITION:
            self.camera_angle = CameraAngle(camera_angle)
            self.set_target_velocity([vel_x, vel_y])

    def set_target_velocity(self, target_vel):
        self.vel_plan = Helpers.validate_velocity_change(self.vel, target_vel)  # list of (vx, vy) steps
        print(f"[Melvin] Velocity plan accepted: {len(self.vel_plan)} steps")
        return True

    def update_velocity(self):
        next_v = self.vel_plan.pop(0)
        self.vel = list(next_v)


melvin = Melvin()


def background_updater():
    while True:
        next_update_time = datetime.now(timezone.utc) + timedelta(seconds=SIM_STEP_DUR)
        melvin.next_sim_step()
        time.sleep(next_update_time.timestamp() - time.time())


threading.Thread(target=background_updater, daemon=True).start()
