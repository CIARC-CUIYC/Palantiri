from dataclasses import dataclass

@dataclass
class Beacon:
    beacon_id: str
    height: int
    width: int