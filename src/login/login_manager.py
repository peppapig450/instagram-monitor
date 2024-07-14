import fnmatch
import logging
import warnings
from collections import OrderedDict
from contextlib import contextmanager
from os import PathLike, getenv
from pathlib import Path
from sqlite3 import OperationalError, connect

from dotenv import load_dotenv
from instaloader.instaloader import (
    ConnectionException,
    Instaloader,
    TwoFactorAuthRequiredException,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class NoCookiesFileFoundWarning(UserWarning):
    pass


class LoginManager:
    def __init__(self, cookiefile: PathLike | None = None) -> None:
        self.cookiefile = cookiefile if cookiefile else None
        self.cookiefile_string = str(self.cookiefile)
        self.instaloader = Instaloader()

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

    def _get_cookie_data_from_db(self, conn):
        try:
            cookie_data = conn.execute(
                "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
            )
        except OperationalError:
            cookie_data = conn.execute(
                "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
            )
        return cookie_data

    def import_session(self):
        logging.info("Using cookies from %s", self.cookiefile_string)

        self.cookiefile_string = str(self.get_cookiefile(self.cookiefile))
        # connect to the database
        conn = connect(self.cookiefile_string)

        try:
            # Fetch cookie data from the database
            cookie_data = self._get_cookie_data_from_db(conn)

            # Initialize Instaloader
            instaloader = Instaloader(max_connection_attempts=1)

            # update session cookies
            instaloader.context._session.cookies.update(cookie_data)

            # Test login
            username = instaloader.test_login()
            if not username:
                logging.error(
                    "Not logged in. Are you logged in successfully in Firefox?"
                )
                raise SystemExit(
                    "Not logged in. Are you logged in successfully in Firefox?"
                )

            logging.info("Imported session cookie for %s.", username)
            instaloader.context.username = username

            return instaloader

        except (ConnectionException, OperationalError) as exc:
            # Handle exceptions
            logging.error("Failed to import session: %s", exc, exc_info=True)
            raise SystemExit(
                "Failed to import session. Check connection or credentials."
            ) from exc

    def load_credentials_from_env(self):
        load_dotenv()
        username = getenv("INSTAGRAM_USERNAME")
        password = getenv("INSTAGRAM_PASSWORD")
        if not username or not password:
            raise SystemExit(
                "INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not set in environment."
            )
        return username, password

    @contextmanager
    def session(self):
        def login_and_yield_instaloader():
            try:
                # Try with cookie file
                self.instaloader = self.import_session()
                return self.instaloader

            except (ConnectionException, OperationalError):
                # Try with environment variables as last resort
                logging.info("Trying to login in with environment variables.")
                username, password = self.load_credentials_from_env()

                try:
                    self.instaloader.login(username, password)
                    logging.info("Logged in as %s", username)
                    return self.instaloader

                except TwoFactorAuthRequiredException as te:
                    logging.error(
                        "Two-factor authentication required. Unable to login."
                    )
                    raise SystemExit(
                        "Two-factor authentication required. Unable to login."
                    ) from te
                except ConnectionException as e:
                    logging.error("Connection failed: %s", e)
                    raise SystemExit(f"Connection failed: {e}") from e

        instaloader_instance = login_and_yield_instaloader()

        yield instaloader_instance
