import random
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Tuple, TypedDict

from src.app.constants import MAP_HEIGHT, MAP_WIDTH


class BeaconObjectiveDict(TypedDict):
    id: int
    name: str
    start: str
    end: str
    decrease_rate: float
    attempts_made: int
    description: str


class BeaconObjectiveFullDict(TypedDict):
    id: int
    name: str
    start: str
    end: str
    decrease_rate: float
    attempts_made: int
    description: str
    beacon_height: int
    beacon_width: int


@dataclass
class BeaconObjective:
    """
    Represents a single beacon objective with a time window, position, and metadata.
    """
    id: int
    name: str
    start: datetime
    end: datetime
    decrease_rate: float
    attempts_made: int
    description: str
    height: int
    width: int

    def to_dict(self) -> BeaconObjectiveDict:
        """
        Serialize the full beacon object into a dictionary.

        Returns:
            Dict[str, object]: A dictionary representation of the beacon.
        """
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "decrease_rate": self.decrease_rate,
            "attempts_made": self.attempts_made,
            "description": self.description,
        }

    @staticmethod
    def create_randomized(rand_beac_id: int) -> "BeaconObjective":
        """
        Create a randomized BeaconObjective with future start/end times and random coordinates.

        Args:
            rand_beac_id (int): The unique ID for the beacon.

        Returns:
            BeaconObjective: A newly created random beacon objective.
        """

        start = datetime.now(timezone.utc) + timedelta(hours=float(random.randint(1, 3)))
        end = start + timedelta(hours=4.0)

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

    def info_to_endpoint(self) -> BeaconObjectiveDict:
        """
        Return a subset of beacon data suitable for public API exposure.

        Returns:
            Dict[str, object]: A trimmed dictionary with essential info.
        """
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat().replace("+00:00", "Z"),
            "decrease_rate": self.decrease_rate,
            "attempts_made": self.attempts_made,
            "description": self.description,
        }

    def is_active(self, now: datetime) -> bool:
        """
        Check if the beacon is currently active.

        Args:
            now (datetime): The current time to check against.

        Returns:
            bool: True if active, False otherwise.
        """
        return self.start <= now <= self.end

    def pos(self) -> Tuple[int, int]:
        """
        Return the (x, y) position of the beacon.

        Returns:
            Tuple[int, int]: Position as (width, height).
        """
        return self.width, self.height
