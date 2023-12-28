#!/usr/bin/env python
"""the main module"""
import csv
import functools
import os
import secrets
import string
import subprocess
import sys
import time
from typing import Callable, Union

import click
import pyperclip
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from constants import DB_FILE_NAME, DB_PATH, PASSWORD_TBL, USERNAME
from database import Database
from function import get_raise, initialization

# Initialize the database by creating necessary tables.
initialization()

# Create an instance from Console
console: Console = Console()


def login(required: bool = True) -> Callable:
    """
    Decorator for handling user login authentication.

    Args:
        required (bool): Flag indicating whether login is required. Default is True.

    Returns:
        callable: Decorator function.

    Usage:
        @login()
        def some_authenticated_function():
            # Your authenticated function logic here
            pass
    """

    def inner(function: Callable) -> Callable:
        """
        Inner decorator function that wraps the authentication logic around the decorated function.

        Args:
            function (callable): The function to be decorated.

        Returns:
            callable: Wrapper function with authentication logic.
        """

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            """
            Wrapper function implementing the authentication logic.

            Args:
                *args: Positional arguments passed to the decorated function.
                **kwargs: Keyword arguments passed to the decorated function.

            Returns:
                Any: Result of the decorated function or False if authentication fails.
            """
            if required:
                # Get current username
                uname = USERNAME
                if not uname:
                    # Prompt user for username
                    uname = click.prompt("Username")
                # Prompt user for password
                password = click.prompt("Password", hide_input=True)

                try:
                    subprocess.run(
                        ["su", uname],
                        input=password.encode(),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                    return function(*args, **kwargs)
                except subprocess.CalledProcessError:
                    msg: str = "Login failed. Incorrect password."
                    console.print(Panel.fit(msg, style="red bold"))
                    sys.exit(1)
                # If login not required, simply call the decorated function
            return function(*args, **kwargs)

        return wrapper

    return inner


@click.group()
def manager():
    """Password Manager CLI tool."""


@manager.command()
@login(required=True)
@click.option("-t", "--timeout", default=5, help="Time out for displaying passwords.")
@click.option(
    "-l",
    "--limit",
    default=10,
    type=int,
    help="Limit the number of results to display.",
)
@click.option(
    "-S", "--search", type=str, help="Search for entries with a specific term."
)
@click.option(
    "-p", "--password-id", type=int, help="Specify the password ID for operations."
)
@click.option(
    "--copy",
    type=click.Choice(["name", "website", "password", "username"]),
    help="Specify what to copy: 'name', 'website', 'username', or 'password'. "
    "Requires the --password-id option.",
    callback=lambda obj, option, value: get_raise(
        click.UsageError,
        f"The --password-id option is required when copying a {value}.",
    )
    if value and not obj.params.get("password_id")
    else value,
)
@click.option("-s", "--show", is_flag=True, help="Show passwords entries.")
def list_passwords(timeout, search, limit, **kwargs):
    """List all password entries."""

    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        # Get the PASSWORD_TBL's columns
        columns = db.columns(table=PASSWORD_TBL)
        rows = db.select(table=PASSWORD_TBL, limit=limit)

        # Create an intance from Table
        table: Table = Table()

        for column in columns:
            table.add_column(column.title(), style="cyan bold")

        for row in rows if bool(rows) else []:
            data: dict = {str(key): value for key, value in zip(columns, row)}

            if search and search not in data["name"]:
                continue

            table.add_row(
                *[
                    "*" * 8
                    if column == "password" and not kwargs.get("show")
                    else str(row)
                    for column, row in data.items()
                ]
            )

        console.print(table)

        if kwargs.get("password_id") and kwargs.get("copy"):
            password = db.select(
                table=PASSWORD_TBL,
                condition={"id": kwargs.get("password_id")},
                mode="fetch-one",
            )

            data: dict = dict(zip(columns, password if bool(password) else []))

            if data[kwargs.get("copy")]:
                pyperclip.copy(data[kwargs.get("copy")])

                txt: str = (
                    "*" * 8
                    if kwargs.get("copy") == "password" and not kwargs.get("show")
                    else data[kwargs.get("copy")]
                )

                console.print(
                    Panel.fit(
                        f"Successfully copied {kwargs.get('copy')}: {txt}",
                        style="green bold",
                    )
                )
            else:
                console.print(
                    Panel.fit(
                        f"Error: No {kwargs.get('copy')} found for the specified password ID.",
                        style="red bold",
                    )
                )

        time.sleep(timeout)
        os.system("clear; ")


@manager.command()
@login(required=True)
@click.option(
    "-p",
    "--password-id",
    type=int,
    required=True,
    help="Specify the password ID for deletion.",
)
@click.option(
    "-f", "--force", is_flag=True, help="Force deletion without confirmation."
)
def delete_password(password_id: int, force: bool = False):
    """Delete a password entry."""

    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        if force:
            click.echo("Force deleting password without confirmation.")
        else:
            click.confirm(
                "Do you really want to delete the password?",
                abort=True,
            )
            click.echo("Deleting password.")

        result = db.delete(table=PASSWORD_TBL, condition={"id": password_id})
        if result:
            msg: str = f"Password entry with ID {password_id} deleted successfully."
            clr: str = "yellow"
        else:
            msg: str = f"Error: Password entry with ID {password_id} not found."
            clr: str = "red"
        console.print(Panel.fit(msg, style=f"{clr} bold"))


@manager.command()
@login(required=True)
def add_password():
    """Add a new password entry."""
    name = click.prompt("Name for the password entry", type=str)
    website = click.prompt("Website URL for the password entry", type=str)
    username = click.prompt("Username for the password entry", type=str)

    password = click.prompt(
        "Password for the password entry",
        type=str,
        hide_input=True,
        confirmation_prompt=True,
    )

    note = click.prompt(
        "Additional notes for the password entry (optional)", type=str, default=""
    )

    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        data: dict = {
            "name": name,
            "website": website,
            "username": username,
            "password": password,
            "note": note,
        }
        result = db.insert(table=PASSWORD_TBL, data=data)

        if result:
            msg, clr = "Password entry added successfully.", "green"
        else:
            msg, clr = "Error: Password entry could not be added.", "red"
        console.print(Panel.fit(msg, style=f"{clr}"))


@manager.command()
@click.option(
    "-p",
    "--password-id",
    type=int,
    required=True,
    help="Specify the password ID for update.",
)
@login(required=True)
def edit_password(password_id):
    """Edit a password entry."""
    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        keys = db.columns(table=PASSWORD_TBL)
        values = db.select(
            table=PASSWORD_TBL, condition={"id": password_id}, mode="fetch-one"
        )
        if isinstance(values, tuple):
            data: Union[dict, None] = dict(zip(keys, values))
        else:
            data: Union[dict, None] = None
        if data:
            name = click.prompt("Name for the password entry", default=data["name"])
            website = click.prompt(
                "Website URL for the password entry", default=data["website"]
            )
            username = click.prompt(
                "Username for the password entry", default=data["username"]
            )

            password = click.prompt(
                "Password for the password entry", default=data["password"]
            )

            note = click.prompt(
                "Additional notes for the password entry (optional)",
                default=data["note"],
            )

            result = db.update(
                table=PASSWORD_TBL,
                values={
                    "name": name,
                    "website": website,
                    "username": username,
                    "password": password,
                    "note": note,
                },
                condition={"id": password_id},
            )

            if result:
                msg, clr = (
                    f"Record with ID {password_id} successfully updated.",
                    "green",
                )
            else:
                msg, clr = f"Error: Record with ID {password_id} not found.", "red"

            console.print(Panel.fit(msg, style=f"{clr} bold"))


@manager.command()
@click.option("--length", type=int, default=12, help="Length of the generated password")
@click.option(
    "--copy-to-clipboard",
    is_flag=True,
    default=False,
    help="Copy the generated password to the clipboard",
)
@login(required=False)
def generate_password(length: int = 12, copy_to_clipboard: bool = False):
    """Generate a random password."""

    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    console.print(Panel(password, style="green bold"), justify="left")

    if copy_to_clipboard:
        pyperclip.copy(password)
        console.print("Password copied to clipboard.\n", style="yellow")


@manager.command()
@login(required=True)
@click.argument("output", type=click.File("wt"))
def export_passwords(output):
    """Export passwords."""

    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        writer = csv.writer(output)
        unique = db.unique_columns(table=PASSWORD_TBL)
        columns = [
            column for column in db.columns(table=PASSWORD_TBL) if column not in unique
        ]
        rows = db.select(table=PASSWORD_TBL, columns=columns)
        writer.writerow(columns)
        if bool(rows):
            writer.writerows(rows)
            msg, clr = f"Passwords exported successfully to: {output.name}", "green"
        else:
            msg, clr = "No passwords found for export.", "red"
        console.print(Panel.fit(msg, style=f"{clr} bold"))


@manager.command()
@login(required=True)
@click.argument("file", type=click.File("rt"))
def import_passwords(file):
    """Import password."""

    with Database(path=DB_PATH, file=DB_FILE_NAME) as db:
        reader = csv.reader(file)
        columns = next(reader)
        rows = list(reader)
        imported: int = 0

        for row in rows:
            data: dict = {str(key): value for key, value in zip(columns, row)}
            result: Union[None, int] = db.insert(table=PASSWORD_TBL, data=data)
            if bool(result):
                imported += 1

        if imported > 0:
            msg, clr = f"Successfully imported {imported} passwords.", "green"
        else:
            msg, clr = "No passwords were imported. Check your CSV file format.", "red"

        console.print(Panel.fit(msg, style=f"{clr} bold"))
