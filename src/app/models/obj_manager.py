from datetime import datetime

from src.app.sim_clock import sim_clock
from src.app.models.obj_beacon import BeaconObjective
from src.app.models.obj_zoned import ZonedObjective


class ObjManager:
    def __init__(self):
        self.obj_list = []
        self.obj_beacon = []
        self.obj_zoned = []

        self._load_initial_objectives()

    # TODO: needs parameter to controller how many and of which type
    def randomize_initial_obj(self):
        pass

    def _load_initial_objectives(self):
        self.zoned = [
            ZonedObjective(
                zo_id=11,
                name="Precise Picture 10",
                start=datetime(2025, 3, 25, 11, 30),
                end=datetime(2025, 3, 25, 13, 30),
                decrease_rate=0.99,
                zone=[12465, 8935, 13065, 9535],
                optic_required="narrow",
                coverage_required=1.0,
                description="For no reason at all, could you take a picture of this area?",
                sprite=None,
                secret=False
            ),
        ]

        self.beacons = [
            BeaconObjective(
                beacon_id=113,
                name="EBT 27",
                start=datetime(2025, 3, 25, 12, 0),
                end=datetime(2025, 3, 25, 19, 0),
                decrease_rate=0.99,
                attempts_made=0,
                description="The Beacons are lit! Gondor calls for aid!",
                height=500,
                width=800

            ),
        ]

    def get_all_objectives(self):
        now = sim_clock.get_time()
        return {
            "zoned_objectives": [z.info_to_endpoint() for z in self.zoned],
            "beacon_objectives": [b.info_to_endpoint() for b in self.beacons]
        }


obj_manager = ObjManager()
