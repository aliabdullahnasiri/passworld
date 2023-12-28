#!/usr/bin/env python
"""
Module: function
Description: This module contains the function for initializing the database tables
"""

from constants import DB_FILE_NAME, DB_PATH
from database import Database as DB


def initialization() -> None:
    """
    Initialize the database by creating necessary tables.

    This function initializes the database by creating one table:
    - 'passwords' table to store password entries.

    Returns:
    None
    """
    with DB(path=DB_PATH, file=DB_FILE_NAME) as db:
        # Create password table
        db.create(
            "passwords",
            ("id", "INTEGER", "PRIMARY", "KEY"),
            ("name", "TEXT", "NOT NULL"),
            ("website", "TEXT", "NOT NULL"),
            ("username", "TEXT"),
            ("password", "TEXT", "NOT NULL"),
            ("note", "TEXT"),
        )


def get_raise(exception_class, *args, **kwargs):
    """
    Raise a custom exception with optional arguments.

    Parameters:
        exception_class (Exception): The custom exception class to be raised.
        *args: Positional arguments to be passed to the exception constructor.
        **kwargs: Keyword arguments to be passed to the exception constructor.

    Raises:
        Exception: An instance of the specified custom exception class.

    Example:
        get_raise(ValueError, "Invalid input", code=42)
    """
    raise exception_class(*args, **kwargs)
