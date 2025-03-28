import random
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from time import timezone

from src.app.constants import MAP_HEIGHT, MAP_WIDTH


@dataclass
class BeaconObjective:
    id: int
    name: str
    start: datetime
    end: datetime
    decrease_rate: float
    attempts_made: int
    description: str
    height: int
    width: int

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "decrease_rate": self.decrease_rate,
            "attempts_made": self.attempts_made,
            "description": self.description,
            "beacon_height": self.height,
            "beacon_width": self.width
        }

    @staticmethod
    def create_randomized(rand_beac_id: int):
        start = datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 3))
        end = start + timedelta(hours=4)

        return BeaconObjective(
            id=rand_beac_id,
            name=f"EBT {rand_beac_id}",
            start=start,
            end=end,
            decrease_rate=0.99,
            attempts_made=0,
            description=f"The Beacon {rand_beac_id} is lit! Gondor calls for aid!",
            height=random.randint(0, MAP_HEIGHT),
            width=random.randint(0, MAP_WIDTH)
        )

    def info_to_endpoint(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "decrease_rate": self.decrease_rate,
            "attempts_made": self.attempts_made,
            "description": self.description,
        }

    def is_active(self, now: datetime):
        return self.start <= now <= self.end

    def pos(self):
        return self.width, self.height
