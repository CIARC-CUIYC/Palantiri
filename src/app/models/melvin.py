import threading
import time
from collections import OrderedDict

from src.app.constants import START_POS, START_VEL, START_BAT, START_FUEL, SatStates, CameraAngle, SIM_STEP_DUR


class Melvin:
    def __init__(self):
        self.pos = START_POS.copy()
        self.vel = START_VEL.copy()
        self.bat = START_BAT
        self.fuel = START_FUEL
        self.state = SatStates.DEPLOYMENT
        self.camera_angle = CameraAngle.NORMAL
        self._lock = threading.Lock()

    def update_position(self):
        with self._lock:
            self.pos[0] += self.vel[0] * SIM_STEP_DUR
            self.pos[1] += self.vel[1] * SIM_STEP_DUR

    def get_observation(self):
        with self._lock:
            return OrderedDict({
                "state": self.state.value,
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
            self.state = SatStates.DEPLOYMENT
            self.camera_angle = CameraAngle.NORMAL

    def update_control(self, vel_x, vel_y, camera_angle, state):
        with self._lock:
            self.vel[0] = vel_x
            self.vel[1] = vel_y
            self.camera_angle = CameraAngle(camera_angle)
            self.state = SatStates(state)


melvin = Melvin()


def background_updater():
    while True:
        melvin.update_position()
        time.sleep(SIM_STEP_DUR)


threading.Thread(target=background_updater, daemon=True).start()
