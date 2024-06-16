import fnmatch
from pathlib import Path
from sqlite3 import connect
from collections import OrderedDict
from os import PathLike
from timeit import Timer


def find_firefox_cookies(base_path=Path.home()):
    for dirpath, dirnames, filenames in base_path.rglob("*/Mozilla/Firefox/Profiles/*"):
        for filename in filenames:
            if filename == "cookies.sqlite":
                return dirpath / filename
    return None


def _find_cookies_files_in_dir_2(directory):
    matching_files = []
    for root, dirs, files in directory.walk():
        print(dirs)

    return matching_files


def _find_cookies_files_in_dir(directory: Path):
    matching_files = [
        Path(root) / file
        for root, dirs, files in directory.walk()
        for file in fnmatch.filter(files, "cookies.sqlite")
    ]

    if len(matching_files) > 1:
        return matching_files[-1]
    else:
        return matching_files[0]


def get_cookies():
    default_cookiepaths = OrderedDict(
        [
            (
                "Windows",
                Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles/",
            ),
            (
                "Darwin",
                Path.home() / "/Library/Application Support/Firefox/Profiles/",
            ),
            ("Default", Path.home() / ".mozilla/firefox/*"),
        ]
    )

    for system, search_path in default_cookiepaths.items():
        if search_path.exists():
            matching_files = _find_cookies_files_in_dir(search_path)
            if matching_files:
                return [matching_files]

    raise SystemExit("No Firefox cookies.sqlite")

    return None


def get_cookies_2():
    default_cookiepaths = OrderedDict(
        [
            (
                "Windows",
                Path.home() / "AppData/Roaming/Mozilla/Firefox/Profiles/",
            ),
            (
                "Darwin",
                Path.home() / "/Library/Application Support/Firefox/Profiles/",
            ),
            ("Default", Path.home() / ".mozilla/firefox/*"),
        ]
    )

    for system, search_path in default_cookiepaths.items():
        if search_path.exists():
            matching_files = _find_cookies_files_in_dir_2(search_path)
            if matching_files:
                return matching_files

    raise SystemExit("No Firefox cookies.sqlite")

    return None


def test_cookies_sqlite(cookies_file: PathLike):
    # Ensure the cookiefile is converted to a string URI
    conn = connect(cookies_file)
    cookie_data = conn.execute(
        "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
    )
    for line in cookie_data.fetchall():
        print(line)


def benchmark():
    # Time measurement setup
    number_of_iterations = 10
    get_cookies_2_timer = Timer(get_cookies_2)
    get_cookies_timer = Timer(get_cookies)

    # Run timeit for both functions with repeat parameter
    get_cookies_2_results = get_cookies_2_timer.repeat(
        repeat=number_of_iterations, number=1
    )
    get_cookies_results = get_cookies_timer.repeat(
        repeat=number_of_iterations, number=1
    )

    # Calculate mean and standard deviation
    import statistics  # Import statistics module

    get_cookies_2_mean = statistics.mean(get_cookies_2_results)
    get_cookies_2_std = statistics.stdev(get_cookies_2_results)

    get_cookies_mean = statistics.mean(get_cookies_results)
    print(get_cookies_2_mean)
    print(get_cookies_2_std)
    get_cookies_std = statistics.stdev(get_cookies_results)

    # Print results with mean and standard deviation
    print(
        "get_cookies_2 execution time (mean ± std. dev.):",
        get_cookies_2_mean,
        "±",
        get_cookies_2_std,
        "seconds per iteration",
    )
    print(
        "get_cookies execution time (mean ± std. dev.):",
        get_cookies_mean,
        "±",
        get_cookies_std,
        "seconds per iteration",
    )

    cookies_file = (
        get_cookies_2() if get_cookies_2_mean < get_cookies_mean else get_cookies()
    )
    if cookies_file:
        print("Found cookies.sqlite:", cookies_file)
    else:
        print("Cookies.sqlite not found in default locations.")


if __name__ == "__main__":
    cookies = get_cookies()
    print(cookies[0])
    test_cookies_sqlite(cookies[0])
