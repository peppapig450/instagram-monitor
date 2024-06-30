import argparse
import logging
import signal

from src.login import LoginManager
from src.monitor import MonitorManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


# TODO: background the thread
def main(usernames_intervals, args: argparse.Namespace):
    login_manager = LoginManager()
    monitor_manager = MonitorManager()

    def signal_handler(sig, frame):
        logging.info("Exiting gracefully...")
        monitor_manager.stop_all()
        raise SystemExit

    signal.signal(signal.SIGINT, signal_handler)

    try:
        with login_manager.session() as insta_loader:
            for username, interval in usernames_intervals.items():
                monitor_manager.add_monitor(username, insta_loader, interval, args)

            input("Press Enter to quit...")
            signal.raise_signal(signal.SIGINT)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt recieved. Exiting...")
        monitor_manager.stop_all()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Instagram monitors for specified usernames."
    )
    parser.add_argument(
        "usernames_intervals",
        metavar="username_interval",
        nargs="+",
        help="Instagram usernames and intervals to monitor (e.g., user1:15 user2:30)",
    )
    parser.add_argument(
        "--no-highlights",
        "-nh",
        action="store_false",
        dest="download_highlights",
        default=True,
        help="Skip downloading highlights.",
    )
    parser.add_argument(
        "--no-stories",
        "-ns",
        action="store_false",
        dest="download_stories",
        default=True,
        help="Skip downloading stories.",
    )

    args = parser.parse_args()

    # Parse usernames and intervals
    usernames_intervals = {}
    for ui in args.usernames_intervals:
        username, interval = ui.split(":")
        usernames_intervals[username] = int(interval)

    main(usernames_intervals, args)
