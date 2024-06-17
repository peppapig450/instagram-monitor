import logging
from collections import deque
from datetime import datetime
from threading import Timer

from login.login_manager import LoginManager
from monitor.monitor import InstagramMonitor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class MonitorInstance:
    def __init__(self, username: str, insta_loader, interval_minutes):
        self.username = username
        self.insta_loader = insta_loader
        self.interval_minutes = interval_minutes
        self.monitor = InstagramMonitor(username, insta_loader)

    def run_monitor(self):
        logging.info("Starting monitor for %s...", self.username)
        self.monitor.run_monitor()
        logging.info(
            "Monitor for %s completed. Rescheduling in %d minutes",
            self.username,
            self.interval_minutes,
        )

    def schedule_next_run(self):
        interval_seconds = self.interval_minutes * 60
        Timer(interval_seconds, self.run_monitor_and_reschedule).start()

    def run_monitor_and_reschedule(self):
        self.run_monitor()
        self.schedule_next_run()
