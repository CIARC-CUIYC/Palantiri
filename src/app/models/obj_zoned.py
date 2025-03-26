import random
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Optional

from src.app.constants import MAP_WIDTH, MAP_HEIGHT

ZONED__DESCRIPTIONS = [
    "Scout the land between the mountains. Something stirs in the shadows.",
    "We need eyes on this region. Use the Palantír if you must — but find out what stirs there.",
    "The seeing-stones have gone silent. A new vision must be recorded from this zone.",
    "The eagles flew over this land not long ago. See what they might have seen.",
    "Fell beasts and black crows cross this sky. Document their path before it's lost.",
    "This valley lies between Rohan and Gondor. We must map its ground before war comes.",
]


@dataclass
class ZonedObjective:
    id: int
    name: str
    start: datetime
    end: datetime
    decrease_rate: float
    zone: list[int]
    optic_required: str
    coverage_required: float
    description: str
    sprite: Optional[str]
    secret: bool

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat().replace("+00:00", "Z"),
            "end": self.end.isoformat() + "Z",
            "decrease_rate": self.decrease_rate,
            "zone": self.zone,
            "optic_required": self.optic_required,
            "description": self.description,
        }

    @staticmethod
    def create_randomized():
        rand_zo_id = random.randint(1, 100)

        start = datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 3))
        end = start + timedelta(hours=random.randint(2, 6))

        rand_x_coord = random.randint(0, MAP_WIDTH)
        rand_y_coord = random.randint(0, MAP_HEIGHT)
        # TODO: Fix hardcoded numbers!
        rand_zone = [rand_x_coord, rand_x_coord + 600, rand_y_coord, rand_y_coord + 600]

        # TODO: Create all types of ZO! (Precise, Wide, etc.)
        return ZonedObjective(
            id=rand_zo_id,
            name=f"Precise Picture {rand_zo_id}",
            start=start,
            end=end,
            decrease_rate=0.99,
            zone=rand_zone,
            optic_required="narrow",  # TODO: Randomize for wide pictures
            coverage_required=1.0,
            description=random.choice(ZONED__DESCRIPTIONS),
            sprite=None,
            secret=False  # TODO: Implement wide images
        )

    def info_to_endpoint(self):
        if self.secret:
            return {
                "id": self.id,
                "name": self.name,
                "start": self.start.isoformat() + "Z",
                "end": self.end.isoformat() + "Z",
                "decrease_rate": self.decrease_rate,
                "optic_required": self.optic_required,
                "description": self.description,
                "secret": True
            }
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat() + "Z",
            "end": self.end.isoformat() + "Z",
            "zone": self.zone,
            "decrease_rate": self.decrease_rate,
            "optic_required": self.optic_required,
            "description": self.description,
            "secret": False

        }

    def is_active(self, now: datetime):
        return self.start <= now <= self.end
