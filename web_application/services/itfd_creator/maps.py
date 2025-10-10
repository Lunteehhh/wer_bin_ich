import os
import sqlite3
from dataclasses import dataclass

from collections import Counter
from collections.abc import Callable

from typing import TypeAlias, Optional

from web_application.core.config import DATA_PATH

"""
Node Categories
0: Normal
1: Connected to another map / 'Entrances'
2: monster_spawner
3: Resource node
"""

Entrances: TypeAlias = list[tuple[int, int, str, int]]


@dataclass(slots=True)
class Node:
    name: str
    category: int
    connections: list[tuple[int, str, int]]
    sentences_first: list[str]
    sentences_last: list[str]
    monsters: list[int]
    items: list[int]
    commands: list[int]
    additional_data: Entrances | None

    def __init__(self,
                 name: str,
                 category: int,
                 connections: list[tuple[int, str, int]] | None,
                 sentences_first: list[str] | None,
                 sentences_last: list[str] | None,
                 monsters: list[int] | None,
                 items: list[int] | None,
                 commands: list[int] | None,
                 additional_data: Entrances | None):
        self.name = name
        self.category = category
        self.connections = connections or []
        self.sentences_first = sentences_first or []
        self.sentences_last = sentences_last or []
        self.monsters = monsters or []
        self.items = items or []
        self.commands = commands or []
        self.additional_data = additional_data


    @property
    def entrances(self) -> Entrances:
        return self.additional_data

    def dictionary(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "connections": self.connections,
            "sentences_first": self.sentences_first,
            "sentences_last": self.sentences_last,
            "monsters": self.monsters,
            "items": self.items,
            "commands": self.commands,
            "additional_data": self.additional_data
        }



@dataclass(slots=True)
class Map:
    name: str
    nodes: list[Node] | list


# Secret Functions
def _convert_string_to_connections(connections: str) -> list[[int, str, int]]:
    if connections == "":
        return []

    nodes: list[[int, str, int]] = []
    connected_nodes = connections.split("\n")

    for _con_node in connected_nodes:
        _con_data = _con_node.split(";")

        nodes.append((int(_con_data[0]), _con_data[1], int(_con_data[2])))

    return nodes


def _convert_string_to_entrances(entrances_string: str
                                 ) -> Entrances:
    if not entrances_string:
        return []

    entrances: list[[int, int, str, int]] = []
    split_entrances = entrances_string.split("\n")

    for _entrance in split_entrances:
        _entrance = _entrance.split(";")

        entrances.append((int(_entrance[0]), int(_entrance[1]), _entrance[2],
                          int(_entrance[3])))

    return entrances


def _convert_connections_to_string(connections: list | tuple) -> str:
    _con_nodes = [f"{val[0]};{val[1]};{val[2]}" for val in connections]

    return "\n".join(_con_nodes)


def _convert_entrances_to_string(entrances: list[[str, str, str, int]]) -> str:
    _con_nodes = [f"{val[0]};{val[1]};{val[2]};{val[3]}" for val in entrances]

    return "\n".join(_con_nodes)


def _node_from_db(name: str,
                  category: int,
                  connections: str | None,
                  sentences_first: str | None,
                  sentences_last: str | None,
                  monsters: str | None,
                  items: str | None,
                  command: str | None,
                  additional_data: str | None) -> Node:
    if connections:
        connections = _convert_string_to_connections(connections)
    else:
        connections = None
    if sentences_first:
        sentences_first = sentences_first.split("\n")
    else:
        sentences_first = None
    if sentences_last:
        sentences_last = sentences_last.split("\n")
    else:
        sentences_last = None
    if monsters:
        monsters = list(map(int, monsters.split(";")))
    else:
        monsters = None
    if items:
        items = list(map(int, items.split(";")))
    else:
        items = None
    if command:
        command = list(map(int, command.split(";")))
    else:
        command = None

    match category:
        case 1:
            _additional_data = _convert_string_to_entrances(additional_data)
        case _:
            _additional_data = None

    return Node(name, category, connections, sentences_first, sentences_last,
                monsters, items, command, _additional_data)


# Service Functions
def init_table(user: str,
               pack_name: str):
    if not user:
        return None

    if not pack_name:
        return None

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS maps("
                       "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "    name TEXT)")

        conn.commit()


def maps(user: str,
         pack_name: str) -> list[[int, str]]:
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM maps")

        results = cursor.fetchall()

    return results


def get(user: str,
        pack_name: str,
        map_id: int) -> list[tuple[int, Node]]:
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        print("dcaujcdoaehqfnoehnqfiodqahiodqadqafdq")
        print(cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())

        cursor.execute(f"SELECT * FROM map_{map_id}")

        results = cursor.fetchall()

    return [(node[0], _node_from_db(*node[1:])) for node in results]


def get_node(user: str,
             pack_name: str,
             map_id: int,
             node_id: int):
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM map_{map_id} WHERE id = ?",
                       (node_id,))

        result = cursor.fetchone()

    return _node_from_db(*result[1:])


def add_map(user: str,
            pack_name: str,
            map_name: str) -> int:
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"

    print(f"\nLIST DIR = {os.listdir(f"{DATA_PATH}/users/{user}")}")
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO maps(name) VALUES (?)",
                       (map_name,))

        map_id = cursor.lastrowid

        cursor.execute(f"CREATE TABLE IF NOT EXISTS map_{map_id}("
                       "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "    name TEXT NOT NULL,"
                       "    category INT,"
                       "    connections TEXT,"
                       "    sentences_first TEXT,"
                       "    sentences_last TEXT,"
                       "    monsters TEXT,"
                       "    items TEXT,"
                       "    commands TEXT,"
                       "    additional_data TEXT)")
        map_id = cursor.lastrowid
        conn.commit()

    return map_id


def add_node(user: str,
             pack_name: str,
             map_id: int,
             name: str,
             category: int,
             connections: list[list[str, str, int | str]] | None = None,
             sentences_first: list[str] = None,
             sentences_last: list[str] = None,
             monsters: list[int] = None,
             items: list[int] = None,
             commands: list[int] = None,
             additional_data: any = None) -> int:

    print(connections)
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"

    # preparing for sql injections
    category = int(category)
    _connections = _convert_connections_to_string(connections)
    _sentences_first = "\n".join(sentences_first) if sentences_first else None
    _sentences_last = "\n".join(sentences_last) if sentences_last else None
    _monsters = ";".join(map(str, monsters)) if monsters else None
    _items = ";".join(map(str, items)) if items else None
    _commands = ";".join(map(str, commands)) if commands else None

    match category:
        case 1:
            _additional_data = _convert_entrances_to_string(additional_data)
        case _:
            _additional_data = ""

    # insert data
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"INSERT INTO map_{map_id}"
            "(name, category, connections, sentences_first, sentences_last, "
            "monsters, items, commands, additional_data)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, category, _connections, _sentences_first,
             _sentences_last, _monsters, _items, _commands, _additional_data))

        node_id = cursor.lastrowid

        # linkage
        cursor.execute(f"CREATE TABLE _map_{map_id}_{node_id}("
                       f"   map INT,"
                       f"   node INT)")

        if items:
            counted_items = Counter(items)
            for item_id, count in counted_items.items():
                cursor.execute(
                    f"INSERT INTO _item_{item_id}_map (map, node, count) "
                    f"VALUES (?, ?, ?)",
                    (map_id, node_id, count))

        if monsters:
            counted_monsters = Counter(monsters)
            for _monster, count in counted_monsters.items():
                cursor.execute(f"INSERT INTO _monster_{_monster}"
                               " (map, node, count)"
                               " VALUES (?, ?, ?)",
                               (map_id, node_id, count))

        for linked_node_id, _, _ in connections:
            print(connections)
            print(f"INSERT INTO _map_{map_id}_{linked_node_id}"
                  "(map, node) VALUES (?, ?)")
            cursor.execute(f"INSERT INTO _map_{map_id}_{linked_node_id}"
                           "(map, node) VALUES (?, ?)",
                           (map_id, node_id))

        if category == 1:
            print(_additional_data)
            for linked_map_id, linked_node_id, _, _ in additional_data:
                cursor.execute(f"INSERT "
                               f"INTO _map_{linked_map_id}_{linked_node_id}"
                               f"(map, node) VALUES (?, ?)",
                               (map_id, node_id))

        conn.commit()

    return node_id


def edit_node(user: str,
              pack_name: str,
              map_id: int,
              node_id: int,
              name: str | None = None,
              category: int | None = None,
              connections: list[[str, str, int]] | None = None,
              sentences_first: list[str] | None = None,
              sentences_last: list[str] | None = None,
              monsters: list[int] | None = None,
              items: list[int] | None = None,
              commands: list[int] | None = None,
              additional_data: any = None):

    print("\n\naddditionalDATA", additional_data)

    def update_linkage_nodes():
        nonlocal cursor, map_id, node_id, connections, category, additional_data

        cursor.execute("SELECT connections, category, additional_data "
                       f"FROM map_{map_id} WHERE id = ?", (node_id,))

        old_connections, old_category, old_additional_data = cursor.fetchone()

        old_connections = _convert_string_to_connections(old_connections)
        for node, _, _ in old_connections:
            cursor.execute(f"DELETE FROM _map_{map_id}_{node} "
                           f"WHERE map = ? AND node = ?", (map_id, node_id))

        print(connections)
        for node, _, _ in connections:
            cursor.execute(f"INSERT INTO _map_{map_id}_{node}(map, node) "
                           f"VALUES (?, ?)", (map_id, node_id))

        if old_category == 1:
            old_additional_data = _convert_string_to_entrances(
                old_additional_data)

            for _map, node, _, _ in old_additional_data:
                cursor.execute(f"DELETE FROM _map_{_map}_{node} "
                               f"WHERE map = ? AND node = ?", (map_id, node_id))

        if category == 1:
            for _map, node, _, _ in additional_data:
                cursor.execute(f"INSERT INTO _map_{_map}_{node}(map, node) "
                               f"VALUES (?, ?)", (map_id, node_id))

    def update_linkage_monster():
        nonlocal cursor, map_id, node_id, name, monsters

        cursor.execute(f"SELECT monsters FROM map_{map_id} WHERE "
                       f"id = ?", (node_id,))

        fetched_monsters, = cursor.fetchone()
        if fetched_monsters:
            fetched_monsters = fetched_monsters[0]
            fetched_monsters = set(fetched_monsters.split(";"))
            for monster_id in fetched_monsters:
                cursor.execute(f"DELETE FROM _monster_{monster_id} "
                               "WHERE map = ? AND node = ?",
                               (map_id, node_id))

        counted_monsters = Counter(monsters)
        for _monster_id, count in counted_monsters.items():
            cursor.execute(f"INSERT INTO _monster_{_monster_id}"
                           f"(map, node, count)"
                           f"VALUES(?, ?, ?)",
                           (map_id, node_id, count))

    def update_linkage_item(_items: list[int]):
        nonlocal cursor, map_id, node_id, items
        cursor.execute(f"SELECT items FROM map_{map_id} WHERE id = ?",
                       (node_id,))

        fetched_items, = cursor.fetchone()
        if fetched_items:
            fetched_items = set(fetched_items[0].split(";"))

            for item_id in fetched_items:
                cursor.execute(f"DELETE FROM _item_{item_id}_map "
                               f"WHERE map = ? AND node = ?",
                               (map_id, node_id))

        counted_items = Counter(items)
        for item_id, count in counted_items.items():
            cursor.execute(f"INSERT INTO _item_{item_id}_map"
                           f"(map, node, count)"
                           f"VALUES (?, ?, ?)",
                           (map_id, node_id, count))

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        update_linkage_nodes()
        update_linkage_monster()
        update_linkage_item(items)

        connections: str = _convert_connections_to_string(connections)
        sentences_first: str = "\n".join(sentences_first)
        sentences_last: str = "\n".join(sentences_last)
        monsters: str = ";".join(map(str, monsters))
        items: str = ";".join(map(str, items))
        commands: str = ";".join(map(str, commands))

        match category:
            case 1:
                additional_data = _convert_entrances_to_string(additional_data)
            case _:
                additional_data = None

        cursor.execute(f"UPDATE map_{map_id} "
                       "SET name = ?,"
                       "    category = ?,"
                       "    connections = ?,"
                       "    sentences_first = ?,"
                       "    sentences_last = ?,"
                       "    monsters = ?,"
                       "    items = ?,"
                       "    commands = ?,"
                       "    additional_data = ?"
                       "WHERE id = ?",
                       (name, category, connections, sentences_first,
                        sentences_last, monsters, items, commands,
                        additional_data, node_id))
        conn.commit()


def delete_node(user: str,
                pack_name: str,
                map_id: int,
                node_id: int):
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # update items and monster linkage
        cursor.execute("SELECT monsters, "
                       "items, category, connections, additional_data "
                       f"FROM map_{map_id}"
                       " WHERE id = ?",
                       (node_id,))

        data = cursor.fetchone()
        monsters, items, category, connections, additional_data = data

        if monsters:
            monsters = set(monsters.split(";"))
            for monster_id in monsters:
                cursor.execute(f"DELETE FROM _monster_{monster_id}"
                               " WHERE map = ? AND node = ?",
                               (map_id, node_id))

        if items:
            items = set(items.split(";"))
            for item_id in items:
                cursor.execute(f"DELETE FROM _item_{item_id}_map "
                               f"WHERE map = ? AND node = ?",
                               (map_id, node_id))

        # update connections and additional_data from other nodes to this
        cursor.execute(f"SELECT * FROM _map_{map_id}_{node_id}")
        results = cursor.fetchall()

        for linked_by_map, linked_by_node in results:
            if linked_by_map == map_id:
                cursor.execute(f"SELECT connections "
                               f"FROM map_{linked_by_map}"
                               " WHERE id = ?", (linked_by_node,))
                connections_2 = cursor.fetchone()[0]

                connections_2 = _convert_string_to_connections(connections_2)
                connections_2 = [
                    node for node in connections_2 if node[0] != node_id
                ]
                connections_2 = _convert_connections_to_string(connections_2)

                cursor.execute(f"UPDATE map_{linked_by_map} "
                               f"SET connections = ?"
                               " WHERE name = ?",
                               (connections_2, linked_by_node))

            else:
                cursor.execute(f"SELECT additional_data "
                               f"FROM map_{linked_by_map}"
                               " WHERE id = ?", (linked_by_node,))
                additional_data = cursor.fetchone()

                additional_data = _convert_string_to_entrances(additional_data)
                additional_data = [
                    ent for ent in additional_data
                    if ent[0] != map_id and ent[1] != node_id
                ]
                additional_data = _convert_entrances_to_string(additional_data)

                cursor.execute(f"UPDATE map_{linked_by_map}"
                               " SET additional_data = ?"
                               " WHERE id = ?",
                               (additional_data, linked_by_node))

        cursor.execute(f"DROP TABLE _map_{map_id}_{node_id}")

        # update connections and additional_data this to other nodes
        print(f"\n connections: {connections}")
        connections = _convert_string_to_connections(connections)
        print(f"\n connections: {connections}")
        for connected_node, _, _ in connections:
            cursor.execute(f"DELETE FROM _map_{map_id}_{connected_node}"
                           " WHERE map = ? AND node = ?", (map_id, node_id))

        if category == 1:
            additional_data = _convert_string_to_entrances(additional_data)
            for connected_map, connected_node, _, _ in additional_data:
                cursor.execute(f"DELETE "
                               f"FROM _map_{connected_map}_{connected_node}"
                               " WHERE map = ? AND node = ?", (map_id, node_id))

        # delete main
        cursor.execute(f"DELETE FROM map_{map_id} "
                       f"WHERE id = ?", (node_id,))

        conn.commit()


def possible_nodes(user: str,
                   pack_name: str) -> dict[int, list[str | list]]:
    possible_nodes_dict = {}
    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM maps")
        results = cursor.fetchall()

        for map_id, map_name in results:
            cursor.execute(f"SELECT id, name FROM map_{map_id}")
            nodes = cursor.fetchall()
            possible_nodes_dict[int(map_id)] = [
                str(map_name),
                nodes
            ]

    print("YEEEEES")
    print(possible_nodes_dict)
    return possible_nodes_dict


def get_node_name(user: str,
                  pack_name: str,
                  map_id: int,
                  node_id: int) -> str:

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        name = cursor.execute(f"SELECT name FROM map_{map_id} WHERE id = ?",
                              (node_id,)).fetchone()[0]

    return name


def get_node_linkages(user: str,
                      pack_name: str,
                      map_id: int,
                      node_id: int) -> list[tuple[int, int, str]]:
    collected_linkages = []

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        fetched_linkages: list[tuple[int, int]] = cursor.execute(
            f"SELECT * FROM _map_{map_id}_{node_id}"
        ).fetchall()

        for link_map_id, link_node_id in fetched_linkages:
            node_name = cursor.execute(
                f"SELECT name FROM map_{link_map_id} WHERE id = ?",
                (link_node_id,)
            ).fetchone()[0]

            collected_linkages.append((link_map_id, link_node_id, node_name))

    return collected_linkages
