import random
from typing import Optional

from PIL.Image import Image
from datetime import datetime, timezone

from ...app.image_loader import apply_map_overlay, remove_map_overlay
from ...app.sim_clock import sim_clock
from ...app.models.obj_beacon import BeaconObjective
from ...app.models.obj_zoned import ZonedObjective


class ObjManager:
    def __init__(self):
        self.obj_list = []
        self.obj_img_map = {}
        self.existing_ids = set()
        self.beacon_list = []
        self.zoned_list = []

    def get_all_objectives(self):
        return {
            "zoned_objectives": [z.info_to_endpoint() for z in self.zoned_list],
            "beacon_objectives": [b.info_to_endpoint() for b in self.beacon_list]
        }

    def create_random_zoned_objective(self, num):
        new_zo_objs = []
        for _ in range(num):
            while True:
                obj_id = random.randint(1, 100)
                if obj_id not in self.existing_ids:
                    new_zo = ZonedObjective.create_randomized(obj_id)
                    self.zoned_list.append(new_zo)
                    self.obj_list.append(self.zoned_list[-1])
                    self.existing_ids.add(new_zo.id)
                    new_zo_objs.append(self.zoned_list[-1])
                    apply_map_overlay(new_zo.overlay)
                    break
        # TODO: create images for objective
        return new_zo_objs

    def create_random_beacon_objective(self, num):
        new_beacons = []
        for _ in range(num):
            while True:
                obj_id = random.randint(1, 100)
                if obj_id not in self.existing_ids:
                    new_bo = BeaconObjective.create_randomized(obj_id)
                    self.zoned_list.append(new_bo)
                    self.obj_list.append(self.zoned_list[-1])
                    self.existing_ids.add(new_bo.id)
                    new_beacons.append(self.zoned_list[-1])
                    break

        return new_beacons

    def create_beacon_from_dict(self, beacon_dict):
        start = datetime.fromisoformat(beacon_dict["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(beacon_dict["end"].replace("Z", "+00:00"))

        new_beac = BeaconObjective(
            id=beacon_dict["id"],
            name=beacon_dict["name"],
            start=start,
            end=end,
            decrease_rate=beacon_dict["decrease_rate"],
            attempts_made=beacon_dict["attempts_made"],
            description=beacon_dict["description"],
            height=beacon_dict["beacon_height"],
            width=beacon_dict["beacon_width"]
        )
        self.obj_list.append(new_beac)
        self.beacon_list.append(new_beac)
        return new_beac

    def create_zoned_from_dict(self, zoned_dict):
        start = datetime.fromisoformat(zoned_dict["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(zoned_dict["end"].replace("Z", "+00:00"))
        overlay = ZonedObjective.get_overlay(zoned_dict["zone"])
        new_zoned = ZonedObjective(
            id=zoned_dict["id"],
            name=zoned_dict["name"],
            start=start,
            end=end,
            decrease_rate=zoned_dict["decrease_rate"],
            zone=zoned_dict["zone"],
            optic_required=zoned_dict["optic_required"],
            coverage_required=zoned_dict["coverage_required"],
            description=zoned_dict["description"],
            sprite=zoned_dict["sprite"],
            secret=zoned_dict["secret"],
            overlay=overlay
        )
        self.obj_list.append(new_zoned)
        self.zoned_list.append(new_zoned)
        apply_map_overlay(new_zoned.overlay)
        # TODO: generate image for objective
        return new_zoned

    def delete_objective_by_id(self, obj_id: int) -> bool:
        for obj in self.obj_list:
            if obj.id == obj_id:
                self.obj_list.remove(obj)
                if isinstance(obj, BeaconObjective):
                    self.beacon_list.remove(obj)
                else:
                    self.obj_img_map.pop(obj.id, None)
                    self.zoned_list.remove(obj)
                    remove_map_overlay(obj.overlay)
                return True
        return False

    def get_obj_img(self, obj_id: int) -> Optional[Image]:
        return self.obj_img_map.get(obj_id, None)


obj_manager = ObjManager()
