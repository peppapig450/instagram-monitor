from collections import deque

from .monitor_instance import MonitorInstance


class MonitorManager:
    def __init__(self) -> None:
        self.monitors: deque[MonitorInstance] = deque()
        self.current_monitor = None

    def add_monitor(self, username: str, insta_loader, interval_minutes, args):
        monitor_instance = MonitorInstance(
            username, insta_loader, interval_minutes, args
        )
        self.monitors.append(monitor_instance)

        if len(self.monitors) == 1:
            self.current_monitor = monitor_instance
            monitor_instance.run_monitor_and_reschedule()

        monitor_instance.schedule_next_run()

    def rotate_and_run_next(self):
        # Rotate the deque to run the next monitor
        self.monitors.rotate(-1)
        self.current_monitor = self.monitors[0]
        self.current_monitor.schedule_next_run()

    def stop_all(self):
        for monitor_instance in self.monitors:
            monitor_instance.cancel_timer()
