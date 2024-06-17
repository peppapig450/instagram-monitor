import argparse
import threading
from monitor import InstagramMonitor
from login_manager import LoginManager

def main(usernames):
    login_manager = LoginManager()
    
    with login_manager.session() as insta_loader:
        monitors = []
        for username in usernames:
            monitor = InstagramMonitor(username, insta_loader)
            monitor.monitor_profile()
        
    input("Press Enter to quit...")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Instagram monitors for specified usernames.")
    parser.add_argument('usernames', metavar='username', nargs='+', help='Instagram usernames to monitor')
    parser.add_argument('--interval', type=int, default=30, help='Interval in minutes between monitor runs (default: 30)')
    
    args = parser.parse_args()
    main(args.usernames)