import sqlite3
from collections import Counter


def check_if_monster_exists(user: str,
			 				pack_name: str,
							monster: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT * FROM monsters WHERE name = ?", (monster,))

		result = cursor.fetchone()

	return True if result else False


def _monster_from_db(name: str,
					 health: int,
					 strength: int,
					 xp: int,
					 items: str,
					 sentences: str) -> [str, int, int, int, list, list]:
	if items:
		items: list[int] = list(map(int, items.split(";")))
	else:
		items = []
	sentences: list[str] = sentences.split("\n") or []

	return name, health, strength, xp, items, sentences


def monsters(user: str,
			 pack_name: str) -> list:
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT * FROM monsters")

		results = cursor.fetchall()

	return [_monster_from_db(*mon) for mon in results]


def possible_monsters(user: str,
					  pack_name: str) -> list:
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT name FROM monsters")

		results = cursor.fetchall()

	return [name for name, in results]


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
		if items:
			counted_items = Counter(items)
			for item, count in counted_items.items():
				cursor.execute(f"INSERT INTO _item_{item}_monster"
							   f"(monster, count)"
							   f"VALUES (?, ?)", (name, count))

			conn.commit()

			cursor.execute(f"CREATE TABLE IF NOT EXISTS _monster_{name}("
						   f"   map TEXT,"
						   f"   node TEXT,"
						   f"   count INTEGER)")

			conn.commit()
		cursor = conn.cursor()
		cursor.execute("INSERT INTO monsters"
					   "(name, health, strength, xp, items, sentences) "
					   "VALUES (?, ?, ?, ?, ?, ?)",
					   (name, health, strength, xp,
						";".join(map(str, items)), "\n".join(sentences)))
		conn.commit()


def get(user: str,
		pack_name: str,
		name: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		cursor.execute("SELECT * FROM monsters WHERE name = ?", (name,))

		result = cursor.fetchone()

	return _monster_from_db(*result)


def edit(user: str,
		 pack_name: str,
		 name: str,
		 health: int,
		 strength: int,
		 xp: int = 0,
		 items: list[int] | None = None,
		 sentences: list[str] | None = None,
		 new_name: str = None):
	def update_linkage(item_ids: list[int],
					   monster: str,
					   new_monster: str | None = None):
		nonlocal cursor

		new_monster = new_monster or monster

		cursor.execute(f"SELECT items FROM monsters WHERE name = ?",
					   (monster,))

		fetched_items, = cursor.fetchone()
		fetched_items = set(fetched_items.split(";"))

		for item_id in fetched_items:
			cursor.execute(f"DELETE FROM _item_{item_id}_monster "
						   f"WHERE monster = ?", (monster,))

		counted_items = Counter(item_ids)
		for item_id, count in counted_items.items():
			cursor.execute(f"INSERT INTO _item_{item_id}_monster"
						   f"(monster, count)"
						   f"VALUES (?, ?)",
						   (new_monster, count))

	def linkage_change_items(monster: str,
							 new_monster: str):
		nonlocal cursor

		cursor.execute(f"SELECT items FROM monsters "
							f"WHERE name = ?",
					   (monster,))

		fetched_items, = cursor.fetchone()
		fetched_items = set(fetched_items.split(";"))

		for _item in fetched_items:
			cursor.execute(f"UPDATE _item_{_item}_monster "
						   f"SET monster = ?"
						   f"WHERE monster = ?",
						   (new_monster, monster))

	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		if items:
			update_linkage(items, name, new_name)
			items: str = ";".join(map(str, items))
		elif new_name:
			linkage_change_items(name, new_name)
			cursor.execute(f"ALTER TABLE _monster_{name} RENAME TO _monster_{new_name}")

		if sentences:
			sentences: str = "\n".join(sentences)

		cursor.execute("UPDATE monsters SET"
					   "    name = COALESCE(?, name), "
					   "    health = COALESCE(?, health), "
					   "    strength = COALESCE(?, strength), "
					   "    xp = COALESCE(?, xp), "
					   "    items = COALESCE(?, items), "
					   "    sentences = COALESCE(?, sentences) "
					   "WHERE name = ?",
					   (new_name, health, strength, xp, items, sentences, name))

		conn.commit()


def delete(user: str,
		   pack_name: str,
		   monster: str):
	path = f"data/users/{user}/itfd_creator/{pack_name}.db"
	with sqlite3.connect(path) as conn:
		cursor = conn.cursor()

		# delete item linkage to this monster
		cursor.execute(f"SELECT items FROM monsters WHERE name = ?",
					   (monster,))

		fetched_items = cursor.fetchone()
		if fetched_items[0] != "":
			fetched_items = set(fetched_items[0].split(";"))

			for item_id in fetched_items:
				cursor.execute(f"DELETE FROM _item_{item_id}_monster "
							   f"WHERE monster = ?", (monster,))

		# delete linkage and monsters in the map
		cursor.execute(f"SELECT map, node"
					   f" FROM _monster_{monster}")
		result = cursor.fetchall()

		map_name: str
		for map_name, node_name in result:
			cursor.execute(f"SELECT monsters FROM map_{map_name} "
						   f"WHERE name = ?", (node_name,))

			fetched_monsters, = cursor.fetchone()
			fetched_monsters = fetched_monsters.split(";")
			fetched_monsters = [x for x in fetched_monsters if x != monster]
			fetched_monsters = ";".join(fetched_monsters)

			cursor.execute(f"UPDATE map_{map_name} "
						   "SET monsters = ?"
						   f"WHERE name = ?",
						   (fetched_monsters, node_name))

		# delete linkage table
		cursor.execute(f"DROP TABLE _monster_{monster}")

		# delete monster
		cursor.execute("DELETE FROM monsters WHERE name = ?", (monster,))
		conn.commit()
