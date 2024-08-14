"""Routines that can be integrated into main control flow."""

import sqlite3
from importlib import resources
from pydbml import PyDBML

DATABASE_NAME = "database.db"
DATABASE_DEFINTION = resources.files("data.resources").joinpath("database.dbml")
DATABASE_RESOURCE = resources.files("data.resources").joinpath(DATABASE_NAME)


def init_database() -> None:
    """Initialise SQLite database if it does not already exist"""
    # Open connection with database
    with resources.as_file(DATABASE_RESOURCE) as database_file:
        if database_file.is_file():
            return

        parsed = PyDBML(DATABASE_DEFINTION)
        init_script = parsed.sql

        connection = sqlite3.connect(database_file)

    # Run init script
    with connection:
        cursor = connection.cursor()
        cursor.executescript(init_script)
        connection.commit()


def get_schema_info():
    with resources.as_file(DATABASE_RESOURCE) as database_file:
        connection = sqlite3.connect(database_file)

    with connection:
        cursor = connection.cursor()
        result = cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        tables = result.fetchall()

        table_schemas = []
        for table in tables:
            result = cursor.execute(f"PRAGMA table_info({table[0]})")
            table_schema = result.fetchall()
            table_schemas.append(table_schema)

    return table_schemas
