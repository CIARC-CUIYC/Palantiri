from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class ZonedObjective:
    zo_id: int
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

    def is_active(self, now: datetime):
        return self.start <= now <= self.end

    def info_to_endpoint(self):
        if self.secret:
            return {
                "id": self.zo_id,
                "name": self.name,
                "start": self.start.isoformat() + "Z",
                "end": self.end.isoformat() + "Z",
                "decrease_rate": self.decrease_rate,
                "optic_required": self.optic_required,
                "description": self.description,
                "secret": True
            }
        return {
            "id": self.zo_id,
            "name": self.name,
            "start": self.start.isoformat() + "Z",
            "end": self.end.isoformat() + "Z",
            "zone": self.zone,
            "decrease_rate": self.decrease_rate,
            "optic_required": self.optic_required,
            "description": self.description,
            "secret": False

        }
