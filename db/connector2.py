import pyodbc
import getpass
from typing import Optional, Tuple

# Try absolute import when installed as a package; fall back for local runs
try:
    from logger import logger
except Exception:  # pragma: no cover
    from logger import logger  # type: ignore


class DatabaseConnector:
    """
    ODBC database connector with interactive DSN selection and credential prompts.
    Features:
      - Optional constructor args (dsn, username, password); otherwise prompts.
      - Retry on connection failure with re-prompt for credentials (and optional DSN change).
      - Convenience helper: query_dataframe(sql) -> pandas.DataFrame
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.dsn = dsn or self._select_dsn()
        self.username = username or input("Enter your database username: ").strip()
        self.password = password or getpass.getpass("Enter your database password: ")
        self.conn: Optional[pyodbc.Connection] = None
        self.cursor: Optional[pyodbc.Cursor] = None

    def _select_dsn(self) -> str:
        """
        Prompts the user to pick a DSN from available ODBC data sources.
        """
        sources = pyodbc.dataSources()  # {dsn_name: driver_name}
        dsn_list = list(sources.items())

        if not dsn_list:
            raise RuntimeError("No DSNs found on this system.")

        print("Available DSNs:")
        for i, (name, driver) in enumerate(dsn_list):
            print(f"[{i}] {name}  ({driver})")

        while True:
            try:
                selection = int(input("Select a DSN by number: "))
                if 0 <= selection < len(dsn_list):
                    selected = dsn_list[selection][0]
                    logger.info(f"User selected DSN: {selected}")
                    return selected
                else:
                    print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")

    def _prompt_credentials(self, prompt_username: bool = False) -> None:
        """
        Re-prompt credentials. By default only asks for password (common case is mistyped password).
        Set prompt_username=True to prompt for username too.
        """
        if prompt_username:
            self.username = input("Enter your database username: ").strip()
        self.password = getpass.getpass("Enter your database password: ")

    def connect(
        self,
        max_attempts: int = 3,
        allow_change_dsn: bool = True,
        reprompt_username: bool = False,
    ) -> Tuple[Optional[pyodbc.Connection], Optional[pyodbc.Cursor]]:
        """
        Attempt to connect up to `max_attempts` times.
        On failure, allow user to re-enter credentials (and optionally change DSN).
        Returns (connection, cursor) or (None, None) on final failure.

        Args:
            max_attempts: number of retries (default 3)
            allow_change_dsn: ask user if they want to change DSN on failure
            reprompt_username: also re-ask for username on each retry (default False: password only)
        """
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            try:
                conn_str = f"DSN={self.dsn};UID={self.username};PWD={self.password}"
                logger.debug(
                    f"Attempting connection (attempt {attempts}) to DSN='{self.dsn}' as user='{self.username}'"
                )
                self.conn = pyodbc.connect(conn_str)
                self.cursor = self.conn.cursor()
                logger.info(f"Connected to DSN '{self.dsn}' successfully on attempt {attempts}.")
                return self.conn, self.cursor

            except pyodbc.Error as e:
                logger.error(f"ODBC error on attempt {attempts}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempts}: {e}")

            # If we reach here, connection failed. Offer retry options.
            print("\nConnection failed.")
            retry = input("Retry? [Y/n]: ").strip().lower()
            if retry == "n":
                break

            if allow_change_dsn:
                change_dsn = input("Change DSN as well? [y/N]: ").strip().lower()
                if change_dsn == "y":
                    try:
                        self.dsn = self._select_dsn()
                    except Exception as e:
                        print(f"Unable to change DSN: {e}")
                        logger.error(f"Unable to change DSN after failure: {e}")

            # Re-prompt credentials (password by default; username optional)
            self._prompt_credentials(prompt_username=reprompt_username)

        print("Unable to connect after multiple attempts.")
        logger.error("Exhausted connection attempts without success.")
        return None, None

    def query_dataframe(self, sql: str):
        """
        Run a SQL query and return the result as a pandas DataFrame.
        Requires an active database connection.
        """
        import pandas as pd  # imported here to avoid making pandas a hard dependency for non-DF use
        if not self.conn:
            raise RuntimeError("No active database connection. Call connect() first.")
        return pd.read_sql(sql, self.conn)

    def close(self):
        """
        Closes the database connection and cursor.
        """
        try:
            if self.cursor:
                self.cursor.close()
                logger.info("Cursor closed.")
            if self.conn:
                self.conn.close()
                logger.info("Connection closed.")
        except Exception as e:
            logger.error(f"Error closing resources: {e}")
