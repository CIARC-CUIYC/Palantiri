import random
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from typing import Optional
from ..helpers import Helpers

from PIL import Image

from ...app.constants import MAP_WIDTH, MAP_HEIGHT, CameraAngle
from ..image_loader import get_obj_img, PADDING

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
    overlay: Optional[Image]

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
    def create_randomized(rand_zo_id: int):
        start = datetime.now(timezone.utc) + timedelta(hours=random.randint(1, 3))
        end = start + timedelta(hours=random.randint(2, 6))

        rand_x_coord = random.randint(0, MAP_WIDTH - 1)
        rand_y_coord = random.randint(0, MAP_HEIGHT - 1)
        # TODO: Fix hardcoded numbers!
        rand_angle = random.choice(list(CameraAngle))
        dy = rand_angle.get_side_length()
        dx_fac = random.randint(1, 4)
        dx = dx_fac * dy

        x_end = Helpers.wrap_coordinate(rand_x_coord + dx, MAP_WIDTH)
        y_end = Helpers.wrap_coordinate(rand_y_coord + dy, MAP_HEIGHT)

        rand_zone = [rand_x_coord, rand_y_coord, x_end, y_end]

        rand_coverage = random.uniform(0.6, 1.0)
        overlay = ZonedObjective.get_overlay(rand_zone)
        return ZonedObjective(
            id=rand_zo_id,
            name=f"Precise Picture {rand_zo_id}",
            start=start,
            end=end,
            decrease_rate=0.99,
            zone=rand_zone,
            optic_required=rand_angle.value(),
            coverage_required=rand_coverage,
            description=random.choice(ZONED__DESCRIPTIONS),
            sprite=None,
            secret=False, # TODO: implement secret objectives?
            overlay=overlay
        )

    @staticmethod
    def get_overlay(zone: list[int]) -> Optional[Image]:
        width = zone[2] - zone[0]
        height = zone[3] - zone[1]
        if width < 0 or height < 0:
            return None
        obj_img = get_obj_img().copy().resize((width, height), Image.Resampling.LANCZOS)
        print(type(obj_img))
        overlay = Image.new("RGBA", (MAP_WIDTH + 2 * PADDING, MAP_HEIGHT + 2 * PADDING), (0, 0, 0, 0))
        insert_pos = (zone[0] + PADDING, zone[1] + PADDING )
        overlay.paste(obj_img, insert_pos)
        if zone[2] < zone[0]:
            # Copy left outer rim to account for wrapping
            crop_box_x = (MAP_WIDTH, PADDING, MAP_WIDTH + PADDING, MAP_HEIGHT + PADDING)
            x_new_pos = (PADDING, PADDING)
            crop_x_slice = overlay.crop(crop_box_x)
            overlay.paste(crop_x_slice, x_new_pos)
        if zone[3] < zone[1]:
            crop_box_y = (PADDING, MAP_HEIGHT, MAP_WIDTH + PADDING, MAP_HEIGHT + PADDING)
            crop_y_slice = overlay.crop(crop_box_y)
            y_new_pos = (PADDING, MAP_HEIGHT + PADDING)
            overlay.paste(crop_y_slice, y_new_pos)
        if zone[2] < zone[0] and zone[3] < zone[1]:
            crop_box_x_y = (MAP_WIDTH, MAP_HEIGHT, MAP_WIDTH + PADDING, MAP_HEIGHT + PADDING)
            crop_x_y_slice = overlay.crop(crop_box_x_y)
            x_y_new_pos = (0, 0)
            overlay.paste(crop_x_y_slice, x_y_new_pos)
        return overlay


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
