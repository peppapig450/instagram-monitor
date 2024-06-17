import argparse
from src.monitor import MonitorManager
from src.login import LoginManager


def main(usernames_intervals):
    login_manager = LoginManager()

    with login_manager.session() as insta_loader:
        monitor_manager = MonitorManager()

        for username, interval in usernames_intervals.items():
            monitor_manager.add_monitor(username, insta_loader, interval)

    input("Press Enter to quit...")


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

    args = parser.parse_args()

    # Parse usernames and intervals
    usernames_intervals = {}
    for ui in args.username_intervals:
        username, interval = ui.split(":")
        usernames_intervals[username] = int(interval)

    main(usernames_intervals)
