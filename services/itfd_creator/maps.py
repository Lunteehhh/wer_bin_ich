import sqlite3
from dataclasses import dataclass

from collections import Counter
from collections.abc import Callable

"""
Node Categories
0: Normal
1: Connected to another map / 'Entrances'
2: monster_spawner
3: Resource node
"""

@dataclass(slots=True)
class Node:
	name: str
	category: int
	connections: list[[str, str, int]]
	sentences_first: list[str] = None
	sentences_last: list[str] = None
	monsters: list[str] = None
	items: list[int] = None
	commands: list[Callable[[any], int]] | list[int] = None
	additional_data: any = None

	@property
	def entrances(self) -> list[[str, str, str, int]]:
		return self.additional_data


@dataclass(slots=True)
class Map:
	name: str
	nodes: list[Node] | list


# Secret Functions
def _convert_string_to_connections(connections: str) -> list[[str, str, int]]:
	if connections == "":
		return []

	nodes: list[[str, str, int]] = []
	connected_nodes = connections.split("\n")

	for _con_node in connected_nodes:
		_con_data = _con_node.split(";")

		nodes.append((_con_data[0], _con_data[1], int(_con_data[2])))

	return nodes


def _convert_string_to_entrances(entrances_string: str
                                 ) -> list[[str, str, str, int]]:
	if entrances_string == "":
		return []

	entrances: list[[str, str, str, int]] = []
	split_entrances = entrances_string.split("\n")

	for _entrance in split_entrances:
		_entrance = _entrance.split(";")

		entrances.append((_entrance[0], _entrance[1], _entrance[2],
						 int(_entrance[3])))

	return entrances


def _convert_connections_to_string(connections: list[[str, str, int]]) -> str:
	_con_nodes = [f"{val[0]};{val[1]};{val[2]}" for val in connections]

	return "\n".join(_con_nodes)


def _convert_entrances_to_string(entrances: list[[str, str, str, int]]) -> str:
	_con_nodes = [f"{val[0]};{val[1]};{val[2]};{val[3]}" for val in entrances]

	return "\n".join(_con_nodes)


def _node_from_db(name: str,
                  category: int,
                  connections: str,
                  sentences_first: str,
                  sentences_last: str,
                  monsters: str,
                  items: str,
				  command: str,
				  additional_data: str) -> Node:
	_connections: list[[str, str, int]]
	_connections = _convert_string_to_connections(connections)
	_sentences_first: list[str] = sentences_first.split("\n")
	_sentences_last: list[str] = sentences_last.split("\n")
	_monsters: list[str] = monsters.split(";")
	_items: list[int] = list(map(int, items.split(";"))) if items else []
	_command: list[int] = list(map(int, command.split(";"))) if command else []

	match category:
		case 1:
			_additional_data = _convert_string_to_entrances(additional_data)
		case _:
			_additional_data = None

	return Node(name, category, _connections, _sentences_first, _sentences_last,
			    _monsters, _items, _command, _additional_data)


# Service Functions
def maps(user: str,
		 pack_name: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT * FROM maps")

		results = cursor.fetchall()

	return [_map[0] for _map in results]


def get(user: str,
		pack_name: str,
		map_name: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute(f"SELECT * FROM map_{map_name}")

		results = cursor.fetchall()

	return [_node_from_db(*node) for node in results]


def add(user: str,
		pack_name: str,
		map_name: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("INSERT INTO maps(name) VALUES (?)",
					   (map_name,))

		cursor.execute(f"CREATE TABLE IF NOT EXISTS map_{map_name}("
					   "    name TEXT PRIMARY KEY,"
					   "    category INT,"
					   "    connections TEXT,"
					   "    sentences_first TEXT,"
					   "    sentences_last TEXT,"
					   "    monsters TEXT,"
					   "    items TEXT,"
					   "    commands TEXT,"
					   "    additional_data TEXT)")
		conn.commit()


def add_node(user: str,
			 pack_name: str,
			 map_name: str,
             node_name: str,
             category: int,
             connections: list[[str, str, int]] | None = None,
             sentences_first: list[str] = None,
             sentences_last: list[str] = None,
             monsters: list[str] = None,
             items: list[int] = None,
             commands: list[int] = None,
             additional_data: any = None):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"

	# preparing for sql injections
	_connections: str = _convert_connections_to_string(connections)
	_sentences_first: str = "\n".join(sentences_first)
	_sentences_last: str = "\n".join(sentences_last)
	_monsters: str = ";".join(monsters)
	_items: str = ";".join(map(str, items))
	_commands: str = ";".join(map(str, commands))

	match category:
		case 1:
			_additional_data = _convert_entrances_to_string(additional_data)
		case _:
			_additional_data = ""

	# insert data
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute(
			f"INSERT INTO map_{map_name}"
			"(name, category, connections, sentences_first, sentences_last, "
			"monsters, items, commands, additional_data)"
			"VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(node_name, category, _connections, _sentences_first,
			 _sentences_last, _monsters, _items, _commands, _additional_data))

		# linkage
		cursor.execute(f"CREATE TABLE _map_{map_name}_{node_name}("
					   f"   map TEXT,"
					   f"   node TEXT)")

		if items:
			counted_items = Counter(items)
			for item_id, count in counted_items.items():
				cursor.execute(
					f"INSERT INTO _item_{item_id}_map (map, node, count) "
					f"VALUES (?, ?, ?)",
					(map_name, node_name, count))

		if monsters:
			counted_monsters = Counter(monsters)
			for _monster, count in counted_monsters.items():
				cursor.execute(f"INSERT INTO _monster_{_monster}"
							   " (map, node, count)"
							   " VALUES (?, ?, ?)",
							   (map_name, node_name, count))

		for linked_node, _, _ in connections:
			cursor.execute(f"INSERT INTO _map_{map_name}_{node_name}"
						   f"(map, node) VALUES (?, ?)",
						   (map_name, linked_node))

		if category == 1:
			for linked_map, linked_node, _, _ in connections:
				cursor.execute(f"INSERT INTO _map_{map_name}_{node_name}"
							   f"(map, node) VALUES (?, ?)",
							   (linked_map, linked_node))

			conn.commit()


def possible_nodes(user: str,
				   pack_name: str) -> dict:
	possible_nodes_dict = {}
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT name FROM maps")
		map_names = cursor.fetchall()

		for map_name, in map_names:
			cursor.execute(f"SELECT name FROM map_{map_name}")
			node_names = cursor.fetchall()
			possible_nodes_dict[map_name] = [name for name, in node_names]

	return possible_nodes_dict



