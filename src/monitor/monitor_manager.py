from collections import deque

from .monitor_instance import MonitorInstance


class MonitorManager:
    def __init__(self) -> None:
        self.monitors = deque()
        self.current_monitor = None

    def add_monitor(self, username: str, insta_loader, interval_minutes):
        monitor_instance = MonitorInstance(username, insta_loader, interval_minutes)
        self.monitors.append(monitor_instance)

        if len(self.monitors) == 1:
            self.current_monitor = monitor_instance
            monitor_instance.schedule_next_run()

    def rotate_and_run_next(self):
        # Rotate the deque to run the next monitor
        self.monitors.rotate(-1)
        self.current_monitor = self.monitors[0]
        self.current_monitor.schedule_next_run()