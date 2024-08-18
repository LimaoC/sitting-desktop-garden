"""Module for interacting with SQLite database"""

import sqlite3

from datetime import datetime
from typing import Any, NamedTuple, Optional
from importlib import resources

from pydbml import PyDBML

RESOURCES = resources.files("data.resources")
DATABASE_DEFINITION = RESOURCES.joinpath("database.dbml")
DATABASE_RESOURCE = RESOURCES.joinpath("database.db")


class User(NamedTuple):
    """Represents a user record in the SQLite database"""

    id_: Optional[int]


class Posture(NamedTuple):
    """Represents a posture record in the SQLite database"""

    id_: Optional[int]
    user_id: int
    prop_good: float
    prop_in_frame: float
    period_start: datetime
    period_end: datetime


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


def save_posture(posture: Posture | tuple) -> None:
    """Stores the posture record in the database.

    Args:
        posture: The posture record to save.
    """
    if posture[0] is not None:
        raise ValueError("Posture record id must be None")

    with _connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO posture VALUES (?, ?, ?, ?, ?, ?);",
            posture,
        )
        connection.commit()


def get_users(num: int = 10) -> list[User]:
    """
    Args:
        num: Number of user to retrieve
        
    Returns:
        num users from the database.
    """
    with _connect() as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM user LIMIT ?", (num,))
        return [User(*record) for record in result.fetchall()]


def get_postures(num: int = 10) -> list[Posture]:
    """
    Args:
        num: Number of posture records to retrieve
        
    Returns:
        num posture records from the database.
    """
    with _connect() as connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM posture LIMIT ?", (num,))
        return [Posture(*record) for record in result.fetchall()]


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
        return sqlite3.connect(
            database_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
