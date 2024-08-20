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
    """Represents a user record in the SQLite database

    Attributes:
        id_: Unique id for the user. Should be set to None when user does not exist in DB.
    """

    id_: Optional[int]


class Posture(NamedTuple):
    """Represents a posture record in the SQLite database

    Attributes:
        id_: Unique id for the posture record. Should be set to None when record does not exist in
            DB.
        user_id: The user for which this posture applies to.
        prop_good: Proportion of time the user is in the frame which the posture is good.
        prop_in_frame: Proportion of time the user is in the frame during the period.
        period_start: Start of the tracked period.
        period_end: End of the tracked period.
    """

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


def save_posture(posture: Posture) -> None:
    """Stores the posture record in the database.

    Args:
        posture: The posture record to save.
    """
    if posture.id_ is not None:
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


def get_user_postures(
    user_id: int,
    num: int = -1,
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
) -> list[Posture]:
    """
    Args:
        user_id: Id of user to get postures for.
        num: Number of posture records to retrieve. Set to -1 to retrieve all records.
        period_start: Only posture records starting at or after this period will be retrieved.
            Leave as None to set no restriction.
        period_end: Only posture records ending at or before this period will be retrieved.
            Leave as None to set no restriction.

    Returns:
        num posture records from the database for the specified user. Retrieves latest inserted
            posture records first.
    """
    params: tuple[int | datetime, ...] = (user_id,)

    # Add limit to query
    limit = ""
    if num != -1:
        limit = " LIMIT ?"
        params = (num,) + params

    # Add period to query
    query_period = ""
    if period_start is not None:
        query_period += " AND DATETIME(period_start) >= DATETIME(?)"
        params += (period_start,)
    if period_end is not None:
        query_period += " AND DATETIME(period_end) <= DATETIME(?)"
        params += (period_end,)

    query = (
        f"SELECT * FROM posture{limit} WHERE user_id = ?{query_period} ORDER BY id DESC"
    )

    with _connect() as connection:
        cursor = connection.cursor()
        result = cursor.execute(query, params)
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
