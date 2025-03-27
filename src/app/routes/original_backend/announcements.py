import time
from datetime import timezone
from flask import Blueprint, Response

from src.app.constants import BEACON_MAX_DETECT_RANGE, SatStates
from src.app.helpers import Helpers
from src.app.models.melvin import melvin
from src.app.models.obj_manager import obj_manager
from src.app.sim_clock import sim_clock

bp = Blueprint('announcements', __name__)


# --- SSE Ping Endpoint ---
@bp.route('/announcements', methods=['GET'])
def stream_beacon_pings():
    def event_stream():
        print("[INFO] Event stream started!")
        while True:
            if not obj_manager.obj_list:
                continue

            now = sim_clock.get_time().replace(tzinfo=timezone.utc)
            start_of_new_min = now.second == 0

            if melvin.melvin_state != SatStates.COMMS:
                continue

            if start_of_new_min:
                melvin_pos_current = melvin.pos
                for beacon in obj_manager.beacon_list:
                    actual_beacon_position = [beacon.width, beacon.height]
                    if beacon.is_active(now):
                        true_distance = Helpers.unwrapped_to(
                            melvin_pos_current,
                            [beacon.width, beacon.height]
                        )

                        if true_distance <= BEACON_MAX_DETECT_RANGE:
                            noisy_distance = Helpers.receive_noisy_measurement(actual_beacon_position,
                                                                               melvin_pos_current)

                            print(f"Sending SSE ping: ID_{beacon.id} DISTANCE_{noisy_distance:.2f}")

                            yield f"data: ID_{beacon.id} DISTANCE_{noisy_distance:.2f}\n\n"

            time.sleep(1)

    return Response(event_stream(), mimetype='text/event-stream')
