from datetime import datetime, timedelta
import threading

class SimulationClock:
    def __init__(self, start_time: datetime):
        self.sim_time = start_time
        self._tick_rate = timedelta(seconds=1)  # real-time = 1s per tick
        self._advance_per_tick = timedelta(seconds=1)  # 1s of sim time per tick

    def start(self):
        def run():
            while True:
                self.sim_time += self._advance_per_tick
                threading.Event().wait(self._tick_rate.total_seconds())

        threading.Thread(target=run, daemon=True).start()

    def get_time(self) -> datetime:
        return self.sim_time

# Singleton instance
sim_clock = SimulationClock(start_time=datetime.now())
sim_clock.start()
