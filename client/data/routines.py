"""Data routines that can be integrated into main control flow."""

import sqlite3
from typing import Any
from importlib import resources

from pydbml import PyDBML

RESOURCES = resources.files("data.resources")
DATABASE_DEFINITION = RESOURCES.joinpath("database.dbml")
DATABASE_RESOURCE = RESOURCES.joinpath("database.db")


def init_database() -> None:
    """Initialise SQLite database if it does not already exist"""
    # Check if database exists
    with resources.as_file(DATABASE_RESOURCE) as database_file:
        if database_file.is_file():
            return

    parsed = PyDBML(DATABASE_DEFINITION)
    init_script = parsed.sql

    # Run init script
    with _connect() as connection:
        cursor = connection.cursor()
        cursor.executescript(init_script)
        connection.commit()


def create_user() -> int:
    """Creates a new user in the database.

    Returns:
        The id of the new user.
    """
    with _connect() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user DEFAULT VALUES;")
        result = cursor.execute("SELECT last_insert_rowid() FROM user;")
        user_id = result.fetchone()[0]
        connection.commit()

    return user_id


def get_schema_info() -> list[list[tuple[Any]]]:
    """Column information on all tables in database.

    Returns:
        Outer list contains table information, inner list contains column
            information tuples.
    """
    with _connect() as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        tables = result.fetchall()

        table_schemas = []
        for table in tables:
            result = cursor.execute(f"PRAGMA table_info({table[0]})")
            table_schema = result.fetchall()
            table_schemas.append(table_schema)

    return table_schemas


def _connect() -> sqlite3.Connection:
    with resources.as_file(DATABASE_RESOURCE) as database_file:
        return sqlite3.connect(database_file)
