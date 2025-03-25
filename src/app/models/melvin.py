import time
import logging
import threading
from collections import OrderedDict

from src.app.constants import *
from src.app.helpers import Helpers

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class Melvin:
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

        self.logger.info("Melvin initialized. Default start values set.")

    def next_sim_step(self):
        with self._lock:
            self.pos[0] += self.vel[0] * SIM_STEP_DUR
            self.pos[1] += self.vel[1] * SIM_STEP_DUR

            if self.transition_time:
                self.transition_time = max(0, self.transition_time - SIM_STEP_DUR)

                if self.transition_time == 0:
                    self.transition_time = None
                    self.melvin_state = self.state_target
                    self.logger.info(f"Melvin state changed to {self.melvin_state.name}")

            if self.melvin_state != self.state_target and self.state_target is not None and self.melvin_state != SatStates.TRANSITION:
                self.melvin_state = SatStates.TRANSITION
                self.logger.info(f"Melvin state changed to {self.melvin_state.name}")
                self.transition_time = Helpers.get_transition_time(self.melvin_state, self.state_target)

            self.bat += SIM_STEP_DUR * Helpers.get_charge_per_sec(self.melvin_state)
            self.bat = Helpers.clamp(self.bat, 0, 100)

    def get_observation(self):
        with self._lock:
            return OrderedDict({
                "state": self.melvin_state.value,
                "angle": self.camera_angle.value,
                "width_x": round(self.pos[0]),
                "height_y": round(self.pos[1]),
                "vx": self.vel[0],
                "vy": self.vel[1],
                "battery": self.bat,
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
            self.vel[0] = vel_x
            self.vel[1] = vel_y
            self.camera_angle = CameraAngle(camera_angle)
            self.state_target = SatStates(state)


melvin = Melvin()


def background_updater():
    while True:
        melvin.next_sim_step()
        time.sleep(SIM_STEP_DUR)


threading.Thread(target=background_updater, daemon=True).start()
