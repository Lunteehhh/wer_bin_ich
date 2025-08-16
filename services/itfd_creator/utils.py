import sqlite3
from pathlib import Path


def get_packs(user: str) -> list[str]:
    directory = Path(f"data/users/{user}/itfd_creator")

    pack_names = [f.stem for f in directory.iterdir() if f.is_file()]

    return pack_names


def add_new_pack(user: str, pack_name: str):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

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
                       "    name TEXT PRIMARY KEY,"
                       "    health INT,"
                       "    strength INT,"
                       "    xp INT,"
                       "    items TEXT,"
                       "    sentences TEXT)")

        cursor.execute("CREATE TABLE IF NOT EXISTS maps("
                       "    name TEXT PRIMARY KEY)")
