from pathlib import Path
import warnings
from collections import OrderedDict
import fnmatch
from os import PathLike
from sqlite3 import OperationalError, connect, Cursor

from instaloader.instaloader import ConnectionException, Instaloader
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class NoCookiesFileFoundWarning(UserWarning):
    pass


class LoginManager:
    def __init__(self, cookiefile: PathLike | None = None, sessionfile=None) -> None:
        self.cookiefile = cookiefile or self.get_cookiefile()
        self.sessionfile = sessionfile

    def get_cookiefile(self, custom_path=None):
        matching_files = []
        if custom_path:
            search_path = Path(custom_path).expanduser()
            if search_path.is_file():
                return search_path
            elif search_path.is_dir():
                matching_files.append(self._find_cookies_files_in_dir(search_path))
                if not matching_files:
                    warnings.warn(
                        f"No `cookies.sqlite` file found in the provided path: {custom_path}.",
                        NoCookiesFileFoundWarning,
                    )
                return matching_files
            else:
                warnings.warn(
                    f"Custom path '{custom_path}' does not exist or is invalid.",
                    NoCookiesFileFoundWarning,
                )

        logger.info(
            "Provided file or directory invalid %s invalid. Falling back to defaults...",
            custom_path,
        )

        # Use ordered dict to preserve order when we iterate to avoid uneccessary searching
        default_cookiepaths = OrderedDict(
            [
                ("Windows", Path.home() / "Appdata/Roaming/Mozilla/Firefox/Profiles/"),
                (
                    "Darwin",
                    Path.home() / "Library/Application Support/Firefox/Profiles/",
                ),
                (
                    "Default",
                    Path.home() / ".mozilla/firefox/",
                ),
            ]
        )

        for _, search_path in default_cookiepaths.items():
            if search_path.exists():
                matching_files = self._find_cookies_files_in_dir(search_path)
                if len(matching_files) > 1:
                    # TODO: figure out how to filter out the developer version one programatically ideally while searching through the files
                    # return the last item in the list for now to get the regular cookies
                    # not the cookies from firefox developer version
                    logging.info(
                        "Found Firefox 'cookies.sqlite' file at: %s", matching_files[-1]
                    )
                    return matching_files[-1]
                logging.info(
                    "Found Firefox 'cookies.sqlite' file at: %s", matching_files[0]
                )
                return matching_files[0]

        raise FileNotFoundError(
            "No Firefox 'cookies.sqlite' file found in any of the specified paths."
        )

    def _find_cookies_files_in_dir(self, directory: Path):
        matching_files = [
            Path(root) / file
            for root, _, files in directory.walk()
            for file in fnmatch.filter(files, "cookies.sqlite")
        ]

        return matching_files

    def get_cookie_data_from_db(self) -> Cursor | None:
        logging.info("Using cookies from %s.", self.cookiefile)

        conn = connect(str(self.cookiefile))
        try:
            cookie_data = conn.execute(
                "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com"
            )
            return cookie_data
        except OperationalError as e:
            logging.warning("First SQL query with baseDomain failed with {e}")
            try:
                cookie_data = conn.execute(
                    "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
                )
                return cookie_data
            except OperationalError as e:
                logging.error(
                    f"Error: {e} while getting cookies from sqlite database.",
                    exc_info=True,
                )
                raise OperationalError(
                    "Something went wrong getting cookies from sqlite database at {str(self.cookiefile)}"
                ) from e

    def import_session(self):
        logging.info(f"Using cookies from {str(self.cookiefile)})")
