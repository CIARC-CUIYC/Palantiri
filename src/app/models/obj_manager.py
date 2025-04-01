import random
from datetime import datetime
from typing import List, Union, Set, Dict

from src.app.models.obj_beacon import BeaconObjective
from src.app.models.obj_zoned import ZonedObjective


class ObjManager:
    """
    Manages creation, storage, and deletion of all objective types in the simulation.
    """

    def __init__(self) -> None:
        self.obj_list: List[Union[BeaconObjective, ZonedObjective]] = []
        self.existing_ids: Set[int] = set()
        self.beacon_list: List[BeaconObjective] = []
        self.zoned_list: List[ZonedObjective] = []

    def get_all_objectives(self) -> Dict[str, List[Dict[str, object]]]:
        """
        Return all objectives, grouped by type.

        Returns:
            Dict[str, List[Dict[str, Any]]]: Grouped objectives for API responses.
        """
        return {
            "zoned_objectives": [z.info_to_endpoint() for z in self.zoned_list],
            "beacon_objectives": [b.info_to_endpoint() for b in self.beacon_list]
        }

    def create_random_zoned_objective(self, num: int) -> List[ZonedObjective]:
        """
        Create a given number of unique randomized ZonedObjectives.

        Args:
            num (int): Number of objectives to generate.

        Returns:
            List[ZonedObjective]: List of created ZonedObjective instances.
        """
        new_zo_objs: List[ZonedObjective] = []
        for _ in range(num):
            while True:
                obj_id = random.randint(1, 100)
                if obj_id not in self.existing_ids:
                    new_zo = ZonedObjective.create_randomized(obj_id)
                    self.zoned_list.append(new_zo)
                    self.obj_list.append(self.zoned_list[-1])
                    self.existing_ids.add(new_zo.id)
                    new_zo_objs.append(self.zoned_list[-1])
                    # apply_map_overlay(new_zo.overlay)
                    break
        # TODO: create images for objective
        return new_zo_objs

    def create_random_beacon_objective(self, num: int) -> List[BeaconObjective]:
        """
        Create a given number of unique randomized BeaconObjectives.

        Args:
            num (int): Number of objectives to generate.

        Returns:
            List[BeaconObjective]: List of created BeaconObjective instances.
        """
        new_beacons = []
        for _ in range(num):
            while True:
                obj_id = random.randint(1, 100)
                if obj_id not in self.existing_ids:
                    new_bo = BeaconObjective.create_randomized(obj_id)
                    self.beacon_list.append(new_bo)
                    self.obj_list.append(self.beacon_list[-1])
                    self.existing_ids.add(new_bo.id)
                    new_beacons.append(self.beacon_list[-1])
                    break

        return new_beacons

    def create_beacon_from_dict(self, beacon_dict: Dict[str, object]) -> BeaconObjective:
        """
        Create a BeaconObjective from dictionary data (e.g., from JSON).

        Args:
            beacon_dict (Dict[str, Any]): Dictionary with beacon data.

        Returns:
            BeaconObjective: The created instance.
        """
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

    def create_zoned_from_dict(self, zoned_dict: Dict[str, object]) -> ZonedObjective:
        """
        Create a ZonedObjective from dictionary data (e.g., from JSON).

        Args:
            zoned_dict (Dict[str, Any]): Dictionary with zoned objective data.

        Returns:
            ZonedObjective: The created instance.
        """
        start = datetime.fromisoformat(zoned_dict["start"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(zoned_dict["end"].replace("Z", "+00:00"))
        # overlay = ZonedObjective.get_overlay(zoned_dict["zone"])
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
            overlay=None
        )
        self.obj_list.append(new_zoned)
        self.zoned_list.append(new_zoned)
        # apply_map_overlay(new_zoned.overlay)
        # TODO: generate image for objective
        return new_zoned

    def delete_objective_by_id(self, obj_id: int) -> bool:
        """
        Delete an objective by its ID.

        Args:
            obj_id (int): The objective ID to delete.

        Returns:
            bool: True if deleted, False if not found.
        """
        remaining_obj = self.obj_list.copy()
        for obj in remaining_obj:
            if obj.id == obj_id:
                self.obj_list.remove(obj)
                if isinstance(obj, BeaconObjective):
                    self.beacon_list.remove(obj)
                else:
                    self.zoned_list.remove(obj)
                    # remove_map_overlay(obj.overlay)
                return True
        return False

    def delete_all(self) -> None:
        """
        Clear all objectives and reset state.
        """
        self.obj_list = []
        self.zoned_list = []
        self.beacon_list = []


obj_manager = ObjManager()
