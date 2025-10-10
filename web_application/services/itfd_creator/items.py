import sqlite3

"""           cat |      a      |    b    |      c      |   d   |    e
quest items:   -1 |             |         |             |       |
normal items:   0 |     ---     |   ---   |             |       | command
Weapons/Tools:  1 | durability  | damage  | type        |       | command
utils:          2 | durability  |         |             |       | command
food:          10 | food        | effect  | fx a        | fx b  | command
drink:         11 | drink       | effect  | fx a        | fx b  | command
Potion:        12 | duration    | effect  | fx a        | fx b  | command
loot bags:     20 | luck        | count   | 100% chance | item  |

type: sword, bow, want
"""


def add(user: str,
        pack_name: str,
        name: str,
        category: int,
        a: int,
        b: int,
        c: int,
        d: int,
        e: int):
    a = a or 0
    b = b or 0
    c = c or 0
    d = d or 0
    e = e or 0

    def _nearest_num() -> int:
        nonlocal cursor

        cursor.execute("SELECT num FROM items")
        result = cursor.fetchall()

        if not result:
            return 0

        i = 0
        for i, (num,) in enumerate(result):
            if i != num:
                return i

        return i + 1

    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        number = _nearest_num()
        cursor.execute("INSERT INTO items("
                       "num, name, category, a, b, c, d, e) "
                       "VALUES (?, ?, ?, ?, ?, ? ,?, ?)",
                       (number, name, category, a, b, c, d, e))

        conn.commit()

        cursor.execute(f"CREATE TABLE _item_{number}_map("
                       "     map TEXT,"
                       "     node TEXT,"
                       "     count INTEGER)")

        cursor.execute(f"CREATE TABLE _item_{number}_monster("
                       "     monster TEXT,"
                       "     count INTEGER)")

        conn.commit()


def get(user: str,
        pack_name: str,
        item_id: int) -> tuple[str, int, int, int, int, int, int]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT name, category, a, b, c, d, e "
                       "FROM items WHERE num = ?", (item_id,))

        item = cursor.fetchone()

    return item


def items(user: str,
          pack_name: str) -> list:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM items")

        results = cursor.fetchall()

    return results


def edit(user: str,
         pack_name: str,
         item_id: int,
         name: str,
         category: int,
         a: int,
         b: int,
         c: int,
         d: int,
         e: int):
    a = a or 0
    b = b or 0
    c = c or 0
    d = d or 0
    e = e or 0

    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("UPDATE items "
                       "SET name = ?,"
                       "    category = ?,"
                       "    a = ?,"
                       "    b = ?,"
                       "    c = ?,"
                       "    d = ?,"
                       "    e = ? "
                       "WHERE num = ?",
                       (name, category, a, b, c, d, e, item_id))

        conn.commit()


def delete(user: str,
           pack_name: str,
           item_id: int):
    item_id_str = str(item_id)
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # delete linkage from monsters
        cursor.execute(f"SELECT monster FROM _item_{item_id}_monster")
        results = cursor.fetchall()

        for monster, in results:
            cursor.execute(f"SELECT items FROM monsters "
                           f"WHERE name = ?", (monster,))

            fetched_items, = cursor.fetchone()
            fetched_items = fetched_items.split(";")
            fetched_items = [x for x in fetched_items if x != item_id_str]
            fetched_items = ";".join(fetched_items)
            cursor.execute(f"UPDATE monsters "
                           f"SET items = ? WHERE name = ?",
                           (fetched_items, monster))

        cursor.execute(f"DROP TABLE _item_{item_id_str}_monster")

        # delete from maps
        cursor.execute(f"SELECT map, node FROM _item_{item_id_str}_map")
        results = cursor.fetchall()

        for map_name, node_name in results:
            cursor.execute(f"SELECT items FROM map_{map_name} "
                           f"WHERE name = ?", (node_name,))

            fetched_items, = cursor.fetchone()
            fetched_items = fetched_items.split(";")
            fetched_items = [x for x in fetched_items if x != item_id_str]
            fetched_items = ";".join(fetched_items)
            cursor.execute(f"UPDATE map_{map_name} "
                           f"SET items = ? WHERE name = ?",
                           (fetched_items, node_name))
        cursor.execute(f"DROP TABLE _item_{item_id_str}_map")

        # ...
        cursor.execute("DELETE FROM items WHERE num = ?",
                       (item_id,))

        conn.commit()


def check_if_items_exists(user: str,
                          pack_name: str,
                          item_ids: list[int]) -> set[int]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        items_ids_set = set(item_ids)

        placeholders = ",".join("?" for _ in items_ids_set)

        cursor.execute(f"SELECT num FROM items WHERE num IN ({placeholders})",
                       tuple(items_ids_set))
        existing_items = set(row[0] for row in cursor.fetchall())

        missing_nums = items_ids_set - existing_items

        return missing_nums


def possible_items(user: str,
                   pack_name: str) -> list[tuple[int, str]]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT num, name FROM items")

        results = cursor.fetchall()

        return results


def get_linkage(user: str,
                pack_name: str,
                item_id: int) -> tuple[list, list]:
    path = f"data/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM _item_{item_id}_monster")
        linkage_monsters = cursor.fetchall()

        cursor.execute(f"SELECT * FROM _item_{item_id}_map")
        linkage_maps = cursor.fetchall()

    return linkage_monsters, linkage_maps


"""
Luck Num
################################################################################
"""


def _convert_mln_to_string(minor_luck_nums: list[int]) -> str:
    return ";".join(map(str, minor_luck_nums))


def _convert_string_to_mln(string: str) -> list[int]:
    if not string:
        return []
    return list(map(int, string.split(";")))


def _convert_items_list_to_string(items_list: list[[int, int]]) -> str:
    items_list = [f"{weight};{item}" for weight, item in items_list]
    return "\n".join(items_list)


def _convert_string_to_items_list(string: str) -> list[[int, int]]:
    if not string:
        return []
    items_list = string.split("\n")
    items_list = map(lambda x: x.split(";"), items_list)

    return [(int(weight), int(item)) for weight, item in items_list]


def _luck_num_from_db(data: tuple[int, str, str]
                      ) -> tuple[int, list[int], list[[int, int]]]:
    num, minors, drops = data

    minors = _convert_string_to_mln(minors)
    drops = _convert_string_to_items_list(drops)

    return num, minors, drops


def get_luck_num(pack: str,
                 user: str,
                 luck_num: int):
    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM luck_nums WHERE num = ?", (luck_num,))

        data = cursor.fetchone()

    return _luck_num_from_db(data)


def get_all_luck_num(pack: str,
                     user: str) -> list[[int, list[int], list[int, int]]]:
    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM luck_nums")

        data = cursor.fetchall()

    return list(map(_luck_num_from_db, data))


def get_possible_luck_nums(pack: str,
                           user: str) -> list[int]:
    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT num FROM luck_nums")

        data = cursor.fetchall()

    return [num for num, in data]


def add_luck_num(user: str,
                 pack: str,
                 luck_num: int,
                 minor_luck_nums: list[int],
                 items_list: [[int, int]]):
    minor_luck_nums = _convert_mln_to_string(minor_luck_nums)
    items_list = _convert_items_list_to_string(items_list)

    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("INSERT INTO luck_nums(num, minor_luck_nums, drops)"
                       "VALUES (?, ?, ?)",
                       (luck_num, minor_luck_nums, items_list))

        cursor.execute(f"CREATE TABLE _luck_num_linkage_{luck_num}("
                       "    num INT PRIMARY KEY)")

        for minor in set(minor_luck_nums):
            cursor.execute(f"INSERT INTO _luck_num_linkage_{minor}(num) "
                           f"VALUES (?)", (luck_num,))


def edit_luck_num(user: str,
                  pack: str,
                  luck_num: int,
                  new_luck_num: int,
                  minor_luck_nums: list[int],
                  items_list: [[int, int]]):
    minor_luck_nums = _convert_mln_to_string(minor_luck_nums)
    items_list = _convert_items_list_to_string(items_list)

    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT minor_luck_nums FROM luck_num WHERE num = ?",
                       (luck_num,))

        old_minors = cursor.fetchone()
        old_minors = set(_convert_string_to_mln(old_minors))
        for minor in old_minors:
            cursor.execute(f"DELETE FROM _luck_num_linkage_{minor} "
                           " WHERE num = ?", (luck_num,))

        cursor.execute("UPDATE luck_nums "
                       "SET num = ?, minor_luck_nums = ?, drops = ? "
                       "WHERE num = ?",
                       (new_luck_num, minor_luck_nums, items_list, luck_num))

        if luck_num != new_luck_num:
            cursor.execute(f"ALTER TABLE _luck_num_linkage_{luck_num}"
                           f"RENAME TO _luck_num_linkage_{new_luck_num}")

        for minor in set(minor_luck_nums):
            cursor.execute(f"INSERT INTO _luck_num_linkage_{minor}(num) "
                           f"VALUES (?)", (new_luck_num,))


def get_luck_num_linkages(user: str,
                          pack: str,
                          luck_num: int) -> list[int]:
    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM _luck_num_linkage_{luck_num}")

        linkages = cursor.fetchall()

    return [link for link, in linkages]


def delete_luck_num(user: str,
                    pack: str,
                    luck_num: int):
    path = f"data/users/{user}/itfd_creator/{pack}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM luck_nums WHERE num = ?", (luck_num,))

        cursor.execute(f"DROP TABLE _luck_num_linkage_{luck_num}")
