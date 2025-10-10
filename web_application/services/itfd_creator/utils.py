import sqlite3
from pathlib import Path
import os
from web_application.services.itfd_creator import maps as maps_service


def get_packs(user: str) -> list[str]:
    directory = Path(f"data/users/{user}/itfd_creator")

    pack_names = [f.stem for f in directory.iterdir() if f.is_file()]

    return pack_names


def add_new_pack(user: str, pack_name: str):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE luck_nums("
                       "    num INTEGER PRIMARY KEY,"
                       "    minor_luck_nums TEXT,"
                       "    drops TEXT)")

        cursor.execute("CREATE TABLE IF NOT EXISTS items("
                       "    num INTEGER PRIMARY KEY,"
                       "    name TEXT, "
                       "    category INTEGER,"
                       "    a INTEGER,"
                       "    b INTEGER,"
                       "    c INTEGER,"
                       "    d INTEGER,"
                       "    e INTEGER)")

        cursor.execute("CREATE TABLE IF NOT EXISTS monsters("
                       "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "    name TEXT,"
                       "    health INT,"
                       "    strength INT,"
                       "    xp INT,"
                       "    items TEXT,"
                       "    sentences TEXT)")

        cursor.execute("CREATE TABLE pack_data("
                       "    description TEXT)")

        maps_service.init_table(user, pack_name)


def delete_pack(user: str, pack_name: str):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"

    os.remove(path)


def get_pack_data(user: str, pack: str) -> tuple[str]:
    path = f"data/users/{user}/itfd_creator/{pack}.db"

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM pack_data")

        return cursor.fetchone()


def edit_description(user: str, pack: str, description: str):
    path = f"data/users/{user}/itfd_creator/{pack}.db"

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("UPDATE pack_data SET description = ?", (description,))

        conn.commit()

