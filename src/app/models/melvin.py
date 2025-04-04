import time
import logging
import threading
from collections import OrderedDict
from datetime import timedelta, datetime, timezone
from logging import Logger
from typing import Optional, List

from src.app.constants import *
from src.app.helpers import Helpers
from src.app.models.obj_manager import obj_manager

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)


class Melvin:
    SIM_DUR_PRINTS: int = 300

    def __init__(self) -> None:
        self.pos: list[float] = START_POS.copy()
        self.vel: list[float] = START_VEL.copy()
        self.bat: float = START_BAT
        self.fuel: float = START_FUEL
        self.state: SatStates = SatStates.DEPLOYMENT
        self.camera_angle: CameraAngle = CameraAngle.NORMAL

        self.state_target: Optional[SatStates] = None
        self.transition_time: float = 0.0

        self.vel_plan: Optional[List[tuple[float, float]]] = None

        self.logger: Logger = logging.getLogger(self.__class__.__name__)
        self.sim_duration: timedelta = timedelta(seconds=0)

        self.logger.info("Melvin initialized. Default start values set.")

    def next_sim_step(self) -> None:
        """
        Advance the simulation by one step.
        """
        self.check_for_transition()
        if self.transition_time > 0.0:
            self.handle_transition_time()

        self.update_pos()
        self.update_battery()

        if self.vel_plan:
            self.update_velocity()
            self.fuel -= FUEL_COST

        self.sim_duration += timedelta(seconds=SIM_STEP_DUR)

        if self.sim_duration.total_seconds() % self.SIM_DUR_PRINTS == 0:
            self.logger.info(f"Simulation duration: {Helpers.format_sim_duration(self.sim_duration)}")

    def update_pos(self) -> None:
        """
        Update Melvin's position using current velocity and simulation time step.
        """
        self.pos[0] += self.vel[0] * SIM_STEP_DUR
        self.pos[1] += self.vel[1] * SIM_STEP_DUR

        self.pos[0] = Helpers.wrap_coordinate(self.pos[0], MAP_WIDTH)
        self.pos[1] = Helpers.wrap_coordinate(self.pos[1], MAP_HEIGHT)

    def update_battery(self) -> None:
        """
        Update battery level based on state and actions.
        """
        if self.vel_plan:
            self.bat += ADD_BAT_COST_BURN
        self.bat += SIM_STEP_DUR * SatStates.get_charge_per_sec(self.state)
        self.bat = Helpers.clamp(self.bat, 0, 100)
        if self.bat <= 0 and self.state_target != SatStates.SAFE:
            self.state_target = SatStates.SAFE
            self.logger.info("Melvin battery empty. Forced transition to safe mode.")

    def handle_transition_time(self) -> None:
        """
        Manage countdown and completion of state transitions.
        """
        self.transition_time = max(0.0, self.transition_time - SIM_STEP_DUR)

        if self.transition_time == 0:
            self.transition_time = 0.0
            self.state = SatStates(self.state_target)
            self.state_target = None
            self.logger.info(f"Melvin state changed to {self.state.name}")

    def check_for_transition(self) -> None:
        """
        Initiate state transition if a valid target state is set.
        """
        if self.state != self.state_target and self.state_target is not None and self.state != SatStates.TRANSITION:
            self.state = SatStates.TRANSITION
            self.vel_plan = []
            self.transition_time = Helpers.get_transition_time(self.state, self.state_target)
            self.logger.info(
                f"Melvin state chang started to {self.state_target.name}. Transition is {self.transition_time}s.")

    def get_observation(self) -> OrderedDict[str, float | int | str | datetime | dict[str, float]]:
        """
        Collect and return current simulation state as an observation.

        Returns:
            OrderedDict[str, Any]: A dictionary of current values.
        """
        return OrderedDict({
            "state": self.state.value,
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

    def reset(self) -> None:
        """
        Reset Melvin to default starting values and clear all objectives.
        """
        self.pos = START_POS.copy()
        self.vel = START_VEL.copy()
        self.bat = START_BAT
        self.fuel = START_FUEL
        self.state = SatStates.DEPLOYMENT
        self.state_target = None
        self.camera_angle = CameraAngle.NORMAL
        obj_manager.delete_all()
        self.logger.info("Melvin reset.")

    def update_state(self, state: SatStates) -> None:
        """
        Set the satellite's next target state.

        Args:
            state (str): Name of the target state.
        """
        if self.state != SatStates.TRANSITION:
            self.state_target = SatStates(state)
            self.logger.info(f"Melvin target state changed to {state}")

    def update_control(self, vel_x: float, vel_y: float, camera_angle: str) -> None:
        """
        Update Melvin's control parameters including velocity and camera angle.

        Args:
            vel_x (float): Desired velocity in x.
            vel_y (float): Desired velocity in y.
            camera_angle (str): Desired camera angle.
        """
        if self.camera_angle != CameraAngle(camera_angle):
            self.logger.info(f"Melvin camera angle changed to {camera_angle}")
            self.camera_angle = CameraAngle(camera_angle)
        if self.vel[0] != vel_x or self.vel[1] != vel_y:
            self.set_target_velocity([vel_x, vel_y])

    def set_target_velocity(self, target_vel: List[float]) -> bool:
        """
        Compute a velocity plan to gradually transition to a new velocity.

        Args:
            target_vel (List[float]): Desired target velocity.

        Returns:
            bool: True when velocity plan has been accepted.
        """
        self.vel_plan = Helpers.validate_velocity_change(self.vel, target_vel)  # list of (vx, vy) steps
        self.logger.info(f"[Melvin] Velocity plan accepted: {len(self.vel_plan)} steps")
        return True

    def update_velocity(self) -> None:
        """
        Apply the next step in the velocity plan.
        """
        if self.vel_plan:
            next_v = self.vel_plan.pop(0)
            self.vel = list(next_v)
        else:
            self.logger.info(f"[Melvin] Velocity plan finished, velocity is {self.vel}.")


melvin = Melvin()


def background_updater() -> None:
    """
    Continuously update the simulation in a background thread.
    """
    while True:
        next_update_time = datetime.now(timezone.utc) + timedelta(seconds=SIM_STEP_DUR)
        melvin.next_sim_step()
        time.sleep(next_update_time.timestamp() - time.time())


threading.Thread(target=background_updater, daemon=True).start()
