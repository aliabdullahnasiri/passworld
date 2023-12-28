#!/usr/bin/env python
"""the database module"""
import functools
import os
import sqlite3 as sql
from functools import wraps
from typing import Dict, List, Literal, Tuple, Union

from rich.console import Console
from rich.panel import Panel


class Database:
    """A class representing an SQLite database interaction."""

    def __init__(self, path: str, file: str) -> None:
        """
        Initialize the Database object.

        Parameters:
        - path (str): Path to the SQLite database.
        - file (str): The SQLite databese file name.
        """

        if not os.path.exists(path=path):
            os.makedirs(path)

        self.connection = sql.connect(f"{path}/{file}")
        self.cursor = self.connection.cursor()
        self.console = Console()

    @staticmethod
    def check(check_type: str = "table"):
        """
        A decorator to check if a table exists before executing a method.

        Parameters:
        - check_type (str): Type of database object to check ('table' by default).

        Returns:
        - wrapper: The decorated method.
        """

        def inner(method):
            @wraps(method)
            def wrapper(self, *args, **kwargs):
                if check_type == "table":
                    table = kwargs.get("table")
                    if table and table not in self.tables():
                        self.console.print(
                            Panel(
                                f"Table '{table}' does not exist.",
                                style="red bold",
                                title="Error",
                            )
                        )

                return method(self, *args, **kwargs)

            return wrapper

        return inner

    @staticmethod
    def error(verbose: Literal["yes", "no"] = "no"):
        """
        A decorator for handling SQLite errors in a method.

        This decorator catches any sqlite3.Error that occurs during the execution
        of the decorated method. If an error is caught, it provides an option to print
        a detailed error message using the Rich library's Panel. The `verbose` parameter
        allows controlling whether the detailed error message is printed.

        Parameters:
        - verbose (Literal["yes", "no"], optional): If "yes", print a detailed error message.
          If "no" (default), do not print detailed error message.

        Returns:
        - callable: The decorated method.

        Example:
        ```python
        class YourClass:
            @staticmethod
            @error(verbose="yes")
            def your_method(self, *args, **kwargs):
                # Your method implementation here
        ```

        In the example above, `your_method` will now have error handling for SQLite errors
        with an option to print a detailed error message based on the value of `verbose`.
        """

        def inner(method):
            @functools.wraps(method)
            def wrapper(self, *args, **kwargs):
                try:
                    result = method(self, *args, **kwargs)
                    return result

                except sql.Error as e:
                    if verbose == "yes":
                        self.console.print(
                            Panel(str(e), style="red bold", title="Error")
                        )
                    return False

            return wrapper

        return inner

    def __enter__(self):
        """
        Enter method for context management.
        """

        return self

    def __exit__(self, *args, **kwargs):
        """
        Exit method for context management.
        """
        # Commit the changes and close the connection
        self.connection.commit()
        self.connection.close()
        return args, kwargs

    @error(verbose="no")
    def tables(self) -> List[str]:
        """
        Get a list of table names in the database.

        Returns:
        - List[str]: List of table names.
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]

    @error(verbose="no")
    def create(self, table: str, *columns):
        """
        Create a table in the database.

        Parameters:
        - table (str): Name of the table to be created.
        - *columns (object): Variable-length arguments representing table columns.

        Returns:
        - None
        """
        query = f"CREATE TABLE IF NOT EXISTS {table} ("
        for column in columns:
            name, data_type, *constraints = column
            constraints_str = " ".join(constraints) if constraints else ""
            query += f"{name} {data_type} {constraints_str},"
        query = query.rstrip(",") + ")"
        self.cursor.execute(query)

    @error(verbose="no")
    @check(check_type="table")
    def insert(
        self, *, table: str, data: Dict[str, Union[str, int, float]]
    ) -> Union[None, int]:
        """
        Insert a new record into the specified table.

        Parameters:
        - table (str): Name of the table to insert into.
        - data (Dict[str, Union[str, int, float]]): Dictionary representing column names and values.

        Returns:
        - None
        """

        columns = ", ".join(data.keys())
        values = ", ".join(["?" for _ in data.values()])
        query = f"INSERT INTO {table} ({columns}) VALUES ({values});"
        self.cursor.execute(query, tuple(data.values()))

        return self.cursor.lastrowid

    @error(verbose="no")
    @check(check_type="table")
    def unique_columns(self, *, table: str) -> List[str]:
        """
        Retrieve a list of column names with a UNIQUE constraint in the specified table.

        Parameters:
        - table (str): The name of the table.

        Returns:
        - List[str]: A list of column names with a UNIQUE constraint.

        Example:
        >>> db = Database("example.db")
        >>> unique_columns = db.unique_columns("your_table_name")
        >>> print("Unique Columns:", unique_columns)

        Note:
        - This method inspects the schema of the table using PRAGMA table_info to
        identify columns with a UNIQUE constraint.
        - The returned list includes only columns with explicit UNIQUE constraints.
        """
        # Execute a query to get information about the table
        self.cursor.execute(f"PRAGMA table_info({table});")

        # Fetch the results
        table_info = self.cursor.fetchall()

        # Extract column names with UNIQUE constraint
        columns = [column[1] for column in table_info if column[5] == 1]

        return columns

    @error(verbose="no")
    @check(check_type="table")
    def columns(self, *, table: str) -> list:
        """
        Get the column names of a table in an SQLite database.

        Parameters:
        - database_path (str): Path to the SQLite database file.
        - table_name (str): Name of the table.

        Returns:
        - List of column names.
        """
        # Execute a query to get the column names
        self.cursor.execute(f"PRAGMA table_info({table})")
        column_info = self.cursor.fetchall()

        # Extract column names from the result
        names = [column[1] for column in column_info]

        return names

    @error(verbose="no")
    @check(check_type="table")
    def select(
        self,
        *,
        table: str,
        columns: Union[None, list] = None,
        condition: Union[dict, None] = None,
        mode: Literal["fetch-one", "fetch-all"] = "fetch-all",
        limit: Union[int, None] = None,
    ) -> Union[List[Tuple], Tuple, None]:
        """
        Select records from the specified table.

        Parameters:
        - table (str): Name of the table to select from.
        - columns (Union[None, list]): Name of columns to select form.
        - condition (dict): Optional SQL condition for filtering.
        - mode (Literal["fetch-one", "fetch-all"])
        - limit (Union[int, None])
        Returns:
        - Union[List[Tuple], Tuple, None]: List of tuples representing the selected records.
        """
        query = "SELECT "
        if columns:
            query += ", ".join(columns)
        else:
            query += "*"
        query += f" FROM {table}"
        if condition:
            query += " WHERE " + " AND ".join(
                [f"`{column}`='{value}'" for column, value in condition.items()]
            )
        if limit and mode == "fetch-all":
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        if mode == "fetch-one":
            return self.cursor.fetchone()
        return self.cursor.fetchall()

    @error(verbose="no")
    @check(check_type="table")
    def update(
        self,
        *,
        table: str,
        values: Dict[str, Union[str, int, float]],
        condition: Union[None, dict] = None,
    ) -> bool:
        """
        Update records in the specified table.

        Parameters:
        - table (str): Name of the table to update.
        - values (Dict[str, Union[str, int, float]]): Dictionary representing column
        names and new values.
        - condition (Union[None, dict]): Optional SQL condition for filtering.

        Returns:
        - bool
        """
        query = f"UPDATE {table} SET "
        query += ", ".join([f"{column} = ?" for column in values.keys()])
        if condition:
            query += " WHERE " + " AND ".join(
                [f"`{column}`='{value}'" for column, value in condition.items()]
            )
        self.cursor.execute(query, tuple(values.values()))
        return bool(self.cursor.rowcount > 0)

    @error(verbose="no")
    @check(check_type="table")
    def delete(
        self,
        *,
        table: str,
        condition: Union[None, dict] = None,
    ) -> bool:
        """
        Delete records from the specified table.

        Parameters:
        - table (str): Name of the table to delete from.
        - condition (Union[None, dict]): Optional SQL condition for filtering rows.

        Returns:
        - bool
        """
        query = f"DELETE FROM {table}"
        if condition:
            query += " WHERE " + " AND ".join(
                [f"`{column}`='{value}'" for column, value in condition.items()]
            )

        self.cursor.execute(query)

        return bool(self.cursor.rowcount > 0)
