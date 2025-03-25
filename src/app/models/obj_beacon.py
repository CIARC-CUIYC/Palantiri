from datetime import datetime
from dataclasses import dataclass


@dataclass
class BeaconObjective:
    beacon_id: int
    name: str
    start: datetime
    end: datetime
    decrease_rate: float
    attempts_made: int
    description: str
    height: int
    width: int


    def is_active(self, now: datetime):
        return self.start <= now <= self.end


    def info_to_endpoint(self):
        return {
            "id": self.beacon_id,
            "name": self.name,
            "start": self.start.isoformat() + "Z",
            "end": self.end.isoformat() + "Z",
            "decrease_rate": self.decrease_rate,
            "attempts_made": self.attempts_made,
            "description": self.description,
        }
