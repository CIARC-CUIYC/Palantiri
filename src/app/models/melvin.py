import time
import logging
import threading
from collections import OrderedDict
from datetime import timedelta

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

        self._lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sim_duration = timedelta(seconds=0)

        self.logger.info("Melvin initialized. Default start values set.")

    def next_sim_step(self):
        with self._lock:
            self.update_pos()
            self.update_battery()

            if self.transition_time:
                self.handle_transition_time()

            self.check_for_transition()
            self.sim_duration += timedelta(seconds=SIM_STEP_DUR)

            if self.sim_duration.total_seconds() % self.SIM_DUR_PRINTS == 0:
                self.logger.info(f"Simulation duration: {Helpers.format_sim_duration(self.sim_duration)}s")

    def update_pos(self):
        self.pos[0] += self.vel[0] * SIM_STEP_DUR
        self.pos[1] += self.vel[1] * SIM_STEP_DUR

        # TODO: Consider check instaed of doing this every time
        Helpers.wrap_coordinate(self.pos[0], MAP_WIDTH)
        Helpers.wrap_coordinate(self.pos[1], MAP_HEIGHT)

    def update_battery(self):
        self.bat += SIM_STEP_DUR * Helpers.get_charge_per_sec(self.melvin_state)
        self.bat = Helpers.clamp(self.bat, 0, 100)
        if self.bat <= 0 and self.state_target != SatStates.SAFE:
            self.state_target = SatStates.SAFE
            self.logger.info("Melvin battery empty. Forced transition to safe mode.")

    def update_vel_and_fuel(self):
        # TODO
        pass

    def handle_transition_time(self):
        self.transition_time = max(0, self.transition_time - SIM_STEP_DUR)

        if self.transition_time == 0:
            self.transition_time = None
            self.melvin_state = self.state_target
            self.logger.info(f"Melvin state changed to {self.melvin_state.name}")

    def check_for_transition(self):
        if self.melvin_state != self.state_target and self.state_target is not None and self.melvin_state != SatStates.TRANSITION:
            self.melvin_state = SatStates.TRANSITION
            self.transition_time = Helpers.get_transition_time(self.melvin_state, self.state_target)
            self.logger.info(
                f"Melvin state changed to {self.melvin_state.name}. Next state is {self.state_target.name} in {self.transition_time}s.")

    def get_observation(self):
        with self._lock:
            return OrderedDict({
                "state": self.melvin_state.value,
                "angle": self.camera_angle.value,
                "width_x": round(self.pos[0]),
                "height_y": round(self.pos[1]),
                "vx": self.vel[0],
                "vy": self.vel[1],
                "battery": round(self.bat, 2),
                "fuel": self.fuel,
            })

    def reset(self):
        with self._lock:
            self.pos = START_POS.copy()
            self.vel = START_VEL.copy()
            self.bat = START_BAT
            self.fuel = START_FUEL
            self.melvin_state = SatStates.DEPLOYMENT
            self.camera_angle = CameraAngle.NORMAL
            self.logger.info("Melvin reset.")

    def update_control(self, vel_x, vel_y, camera_angle, state):
        with self._lock:
            if self.melvin_state == SatStates.ACQUISITION:
                self.vel[0] = vel_x
                self.vel[1] = vel_y
                self.camera_angle = CameraAngle(camera_angle)
            # TODO: this has to be placed in the actual API call
            if Helpers.validate_mode_change(self.melvin_state, state):
                self.state_target = SatStates(state)


melvin = Melvin()


def background_updater():
    while True:
        melvin.next_sim_step()
        time.sleep(SIM_STEP_DUR)


threading.Thread(target=background_updater, daemon=True).start()
