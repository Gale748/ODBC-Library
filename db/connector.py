import pyodbc
import getpass
from typing import Optional, Tuple

from logger import logger  # shared logger setup

class DatabaseConnector:
    def __init__(self):
        self.dsn = self._select_dsn()
        self.username = input("Enter your database username: ")
        self.password = getpass.getpass("Enter your database password: ")
        self.conn = None
        self.cursor = None

    def _select_dsn(self) -> str:
        """
        Prompts the user to pick a DSN from available ODBC data sources.
        """
        sources = pyodbc.dataSources()
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

    def connect(self) -> Tuple[Optional[pyodbc.Connection], Optional[pyodbc.Cursor]]:
        """
        Connects using the selected DSN and user-provided credentials.
        """
        try:
            conn_str = f"DSN={self.dsn};UID={self.username};PWD={self.password}"
            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to DSN '{self.dsn}' successfully.")
            return self.conn, self.cursor
        except pyodbc.Error as e:
            logger.error(f"ODBC error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        return None, None

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