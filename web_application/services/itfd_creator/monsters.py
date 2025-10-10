import sqlite3
from collections import Counter
from typing import TypeAlias


Monster: TypeAlias = [str, int, int, int, list, list]


def check_if_monster_exists(user: str,
                            pack_name: str,
                            monster_id: int):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,))

        result = cursor.fetchone()

    return True if result else False


def _monster_from_db(name: str,
                     health: int,
                     strength: int,
                     xp: int,
                     items: str,
                     sentences: str) -> tuple[str, int, int, int, list, list]:
    if items:
        items: list[int] = list(map(int, items.split(";")))
    else:
        items = []

    sentences: list[str] = sentences.split("\n") if sentences else []

    return name, health, strength, xp, items, sentences


def monsters(user: str,
             pack_name: str
             ) -> list:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM monsters")

        results = cursor.fetchall()

    return [(mon[0], *_monster_from_db(*mon[1:])) for mon in results]


def possible_monsters(user: str,
                      pack_name: str) -> list[[int, str]]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM monsters")

        results = cursor.fetchall()

    return results


def add(user: str,
        pack_name: str,
        name: str,
        health: int,
        strength: int,
        xp: int = 0,
        items: list[int] | None = None,
        sentences: list[str] | None = None):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO monsters"
                       "(name, health, strength, xp, items, sentences) "
                       "VALUES (?, ?, ?, ?, ?, ?)",
                       (name, health, strength, xp,
                        ";".join(map(str, items)), "\n".join(sentences)))

        monster_id = cursor.lastrowid

        if items:
            counted_items = Counter(items)
            for item, count in counted_items.items():
                cursor.execute(f"INSERT INTO _item_{item}_monster"
                               f"(monster, count)"
                               f"VALUES (?, ?)", (monster_id, count))

        cursor.execute(f"CREATE TABLE IF NOT EXISTS _monster_{monster_id}("
                       f"   map INT,"
                       f"   node INT,"
                       f"   count INT)")

        conn.commit()


def get(user: str,
        pack_name: str,
        monster_id: int) -> Monster:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM monsters WHERE id = ?", (monster_id,))

        result = cursor.fetchone()

    if result:
        return _monster_from_db(*result[1:])
    else:
        return None


def edit(user: str,
         pack_name: str,
         monster_id: int,
         name: str,
         health: int,
         strength: int,
         xp: int = 0,
         items: list[int] | None = None,
         sentences: list[str] | None = None):
    def update_linkage():
        nonlocal cursor

        cursor.execute(f"SELECT items FROM monsters WHERE id = ?",
                       (monster_id,))

        fetched_items = cursor.fetchone()[0]
        if fetched_items:
            fetched_items = set(fetched_items.split(";"))

            for item_id in fetched_items:
                cursor.execute(f"DELETE FROM _item_{item_id}_monster "
                               f"WHERE monster = ?", (monster_id,))

        counted_items = Counter(items)
        for item_id, count in counted_items.items():
            cursor.execute(f"INSERT INTO _item_{item_id}_monster"
                           f"(monster, count)"
                           f"VALUES (?, ?)",
                           (monster_id, count))

    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        update_linkage()

        if items is not None:
            items: str = ";".join(map(str, items))

        if sentences:
            sentences = "\n".join(sentences)
        else:
            sentences = None

        cursor.execute("UPDATE monsters SET"
                       "    name = ?, "
                       "    health = ?, "
                       "    strength = ?, "
                       "    xp = ?, "
                       "    items = ?, "
                       "    sentences = ? "
                       "WHERE id = ?",
                       (name, health, strength, xp, items, sentences,
                        monster_id))

        conn.commit()


def delete(user: str,
           pack_name: str,
           monster_id: int):
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # delete item linkage to this monster
        cursor.execute(f"SELECT items FROM monsters WHERE id = ?",
                       (monster_id,))

        fetched_items = cursor.fetchone()[0]
        if fetched_items and fetched_items[0] != "":
            print(fetched_items)
            fetched_items = set(fetched_items[0].split(";"))

            for item_id in fetched_items:
                cursor.execute(f"DELETE FROM _item_{item_id}_monster "
                               f"WHERE monster = ?", (monster_id,))

        # delete linkage and monsters in the map
        cursor.execute(f"SELECT map, node"
                       f" FROM _monster_{monster_id}")
        result = cursor.fetchall()

        monster_id_str = str(monster_id)
        for map_id, node_id in result:
            cursor.execute(f"SELECT monsters FROM map_{map_id} "
                           f"WHERE id = ?", (node_id,))

            fetched_monsters, = cursor.fetchone()
            fetched_monsters = fetched_monsters.split(";")
            fetched_monsters = [
                x for x in fetched_monsters
                if x != monster_id_str
            ]
            fetched_monsters = ";".join(fetched_monsters)

            cursor.execute(f"UPDATE map_{map_id} "
                           "SET monsters = ?"
                           f"WHERE id = ?",
                           (fetched_monsters, node_id))

        # delete linkage table
        cursor.execute(f"DROP TABLE _monster_{monster_id}")

        # delete monster
        cursor.execute("DELETE FROM monsters WHERE id = ?", (monster_id,))
        conn.commit()


def get_linkage(user: str,
                pack_name: str,
                monster_id: int) -> list[tuple[int, int, int]]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM _monster_{monster_id}")
        linkage_maps = cursor.fetchall()

    return linkage_maps


def selectable_monsters(user: str,
                        pack_name: str) -> list[tuple[int, str]]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT id, name FROM monsters")
        results = cursor.fetchall()

    return results

