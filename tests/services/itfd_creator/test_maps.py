import os
import pathlib
import sqlite3
import pytest
import shutil

from web_application.core.config import DATA_PATH

from web_application.services.itfd_creator.maps import (
    Node,
    _convert_connections_to_string,
    _convert_entrances_to_string,
    _convert_string_to_connections,
    _convert_string_to_entrances,
    _node_from_db,

    add_map,
    delete_node,
)

AVAILABLE_PACK_TABLES = [
    ('items',),
    ('map_1',),
    ('map_2',),
    ('maps',),
    ('monsters',),
    ('sqlite_sequence',)
]


def _init_empty_pack(user: str,
                     pack: str):
    if not os.path.exists(f"{DATA_PATH}/users/{user}"):
        os.mkdir(f"{DATA_PATH}/users/{user}")
        os.mkdir(f"{DATA_PATH}/users/{user}/itfd_creator")

    shutil.copyfile("../../templates/empty_pack.db",
                    f"{DATA_PATH}/users/{user}/itfd_creator/{pack}.db")


def _init_pack(user: str,
               pack: str):
    if not os.path.exists(f"{DATA_PATH}/users/{user}"):
        os.mkdir(f"{DATA_PATH}/users/{user}")
        os.mkdir(f"{DATA_PATH}/users/{user}/itfd_creator")

    shutil.copyfile("../../templates/pack.db",
                    f"{DATA_PATH}/users/{user}/itfd_creator/{pack}.db")


def _remove_pack(pack: str,
                 user: str):
    os.remove(f"{DATA_PATH}/users/{user}/itfd_creator/{pack}.db")


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("", []),
        ("1;door;2", [(1, "door", 2)]),
        ("1;door;2\n3;path;4", [(1, "door", 2), (3, "path", 4)])
    ]
)
def test_convert_string_to_connections(input_str, expected):
    assert _convert_string_to_connections(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("", []),
        ("1;32;House;0", [(1, 32, "House", 0)]),
        ("3;43;New House;32\n4;1;Bridge;0",
         [(3, 43, "New House", 32), (4, 1, "Bridge", 0)])
    ]
)
def test_convert_string_to_entrances(input_str, expected):
    assert _convert_string_to_entrances(input_str) == expected


@pytest.mark.parametrize(
    "input_connections, expected",
    [
        ([], ""),
        ([(1, "new", 23)], "1;new;23"),
        ([(32, "testString", 43), (3, "Rot", 543)],
         "32;testString;43\n3;Rot;543")
    ]
)
def test_convert_connections_to_string(input_connections, expected):
    assert _convert_connections_to_string(input_connections) == expected


@pytest.mark.parametrize(
    "input_entrances, expected",
    [
        ([], ""),
        ([(32, 32324, "Blau", 0)], "32;32324;Blau;0"),
        ([(1, 42, "GelbGrau", 34), (4, 56, "Lila", 64)],
         "1;42;GelbGrau;34\n4;56;Lila;64")
    ]
)
def test_convert_entrances_to_string(input_entrances, expected):
    assert _convert_entrances_to_string(input_entrances) == expected


@pytest.mark.parametrize(
    "input_node_data, expected",
    [
        (
            ("New", 0, "", "", "", "", "", "", ""),
            Node("New", 0, None, None, None, None, None, None, None)
        ),
        (
            ("New2", 2, None, None, None, None, None, None, None),
            Node("New2", 2, None, None, None, None, None, None, None)
        ),
        (
            (
                "node", 1,
                "132;Gold;3",
                "cool", "exit",
                "1", "434", "3243", "9;43;Jut;3"
            ),
            Node(
                "node", 1,
                [(132, "Gold", 3)],
                ["cool"], ["exit"],
                [1], [434], [3243],
                [(9, 43, "Jut", 3)]
            )
        ),
        (
            (
                "test", 1,
                "132;Gold;3\n56;Wasser;0",
                "cool $\nCash", "exit\nfe",
                "1;3;42", "434;55", "3243;434;34",
                "9;43;Jut;3\n43;3;Hallo;4"
            ),
            Node(
                "test", 1,
                [(132, "Gold", 3), (56, "Wasser", 0)],
                ["cool $", "Cash"], ["exit", "fe"],
                [1, 3, 42], [434, 55], [3243, 434, 34],
                [(9, 43, "Jut", 3), (43, 3, "Hallo", 4)]
            )
        ),
    ]
)
def test_node_from_db(input_node_data, expected):
    assert _node_from_db(*input_node_data) == expected


@pytest.mark.parametrize(
    "user, pack, map_names, expected_maps, expected_tables",
    [
        (
            "test_maps", "test_add_map",
            ["test_1", "test_2"],
            [(1, "test_1"), (2, "test_2")],
            [('items',), ('map_1',), ('map_2',), ('maps',), ('monsters',),
             ('sqlite_sequence',)]
        )
    ]
)
def test_add_map(user: str, pack: str,
                 map_names: [str],
                 expected_maps, expected_tables):
    _init_empty_pack(user, pack)

    for map_name in map_names:
        add_map(user, pack, map_name)

    with sqlite3.connect(
        f"{DATA_PATH}/users/{user}/itfd_creator/{pack}.db") as conn:
        cursor = conn.cursor()

        maps = cursor.execute("SELECT * FROM maps").fetchall()
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

        print(expected_maps, "\n", maps, "\n",
              sorted(expected_tables), "\n", sorted(tables))

        assert (expected_maps == maps
                and sorted(expected_tables) == sorted(tables))

        _remove_pack(pack, user)


@pytest.mark.parametrize(
    "user, pack, map_id, expected_value",
    [
        (
            "test_user", "test_pack", 1,
            [
                (1,
                 Node("afca", 0, [(2, "new", 0)], ["cup"], None, [1, 1], None,
                      None, None)),
                (2,
                 Node("New", 0, [(1, "afca", 0), (3, "three", 12)], None, None,
                      [2], [0], None, None)),
                (3,
                 Node("three", 0, None, ["news"], ["schoen"], None, [0, 0, 2],
                      None, None))
            ]
        ),
        (
            "test_user", "test_pack", 2,
            [
                (1, Node("start", 0, [(2, "next", 0)], None, None, [1, 2], [0],
                         None, None)),
                (2, Node("test_map2", 1, [(1, "last", 0)], None, None, [2], [2],
                         None, [(1, 2, "MapOne", 33)])),
            ]
        )
    ]
)
def test_get(user: str,
             pack: str,
             map_id: int,
             expected_value: list[int, Node]):
    from web_application.services.itfd_creator.maps import get
    _init_pack(user, pack)

    x = get(user, pack, map_id)

    print(x, expected_value)
    assert x == expected_value

    # _remove_pack(pack, user)


@pytest.mark.parametrize(
    "user, pack, map_id, node_id, expected_node",
    [
        (
            "test_user", "test_get_node", 1, 2,
            Node("New", 0, [(1, "afca", 0), (3, "three", 12)], None, None, [2],
                 [0], None, None),
        ),
        (
            "test_user", "test_get_node", 2, 1,
            Node("start", 0, [(2, "next", 0)], None, None, [1, 2], [0], None,
                 None),
        )
    ]
)
def test_get_node(user: str,
                  pack: str,
                  map_id: int,
                  node_id: int,
                  expected_node: Node):
    from web_application.services.itfd_creator.maps import get_node
    _init_pack(user, pack)

    x = get_node(user, pack, map_id, node_id)

    assert x == expected_node


@pytest.mark.parametrize(
    "user, pack, map_name, expected_value, _start",
    [
        ("test_user", "test_add_map", "New Map 3", 3, True),
        ("test_user", "test_add_map", "New Map 4", 4, False),
    ]
)
def test_add_map(user: str,
                 pack: str,
                 map_name: str,
                 expected_value: int,
                 _start: bool):
    from web_application.services.itfd_creator.maps import add_map

    if _start:
        _init_pack(user, pack)

    x = add_map(user, pack, map_name)

    assert x == expected_value


@pytest.mark.parametrize(
    "user, pack_name, "

    "map_id, "

    "name, "
    "category, "
    "connections, "
    "sentence_first, "
    "sentence_last, "
    "monsters, "
    "items, "
    "commands, "
    "additional_data, "

    "expected_value, "
    "sql_strings",
    [
        (
            "test_user", "test_add_node",

            1,

            "Add first Node",
            1,
            [(1, "afca", 0), (2, "sec", 12)],
            ["hallo", "bye"],
            ["ciao"],
            [1, 2, 2],
            [0, 2, 0],
            [1, 2, 32],
            [(2, 1, "2first", 0), (2, 2, "2second", 12)],

            4,
            [
                "SELECT EXISTS(SELECT * FROM map_1 "
                "WHERE id = 4 "
                "AND name = 'Add first Node' "
                "AND category = 1 "
                "AND connections = '1;afca;0\n2;sec;12' "
                "AND sentences_first = 'hallo\nbye' "
                "AND sentences_last = 'ciao' "
                "AND monsters = '1;2;2' "
                "AND items = '0;2;0' "
                "AND commands = '1;2;32' "
                "AND additional_data = '2;1;2first;0\n2;2;2second;12')",

                "SELECT EXISTS(SELECT 1 FROM sqlite_master "
                "WHERE type='table' AND name='_map_1_4')",

                "SELECT COUNT(*) = 2 FROM _map_1_1",

                "SELECT COUNT(*) = 3 FROM _map_1_2",

                "SELECT COUNT(*) = 1 FROM _map_1_3",

                "SELECT COUNT(*) = 2 FROM _map_2_1",

                "SELECT COUNT(*) = 2 FROM _map_2_2",

                "SELECT EXISTS(SELECT * FROM _map_1_1 "
                "WHERE map='1' AND node='4')",

                "SELECT EXISTS(SELECT * FROM _map_1_2 "
                "WHERE map='1' AND node='4')",

                "SELECT EXISTS(SELECT * FROM _map_1_3 "
                "WHERE map='1' AND node='4') = 0",

                "SELECT EXISTS(SELECT * FROM _map_2_1 "
                "WHERE map='1' AND node='4')",

                "SELECT EXISTS(SELECT * FROM _map_2_2 "
                "WHERE map='1' AND node='4')",

                "SELECT COUNT(*) = 3 FROM _monster_1",
                "SELECT COUNT(*) = 3 FROM _monster_2",
                "SELECT COUNT(*) = 0 FROM _monster_3",

                "SELECT EXISTS(SELECT count = 1 FROM _monster_1 "
                "WHERE map = 1 AND node = 4)",

                "SELECT EXISTS(SELECT count = 2 FROM _monster_2 "
                "WHERE map = 1 AND node = 4)",

                "SELECT COUNT(*) = 4 FROM _item_0_map",

                "SELECT COUNT(*) = 3 FROM _item_2_map",

                "SELECT EXISTS(SELECT count = 1 FROM _item_0_map "
                "WHERE map = 1 AND node = 4)",

                "SELECT EXISTS(SELECT count = 2 FROM _item_2_map "
                "WHERE map = 1 AND node = 4)",
            ]
        )
    ]
)
def test_add_node(user: str,
                  pack_name: str,
                  map_id: int,
                  name: str,
                  category: int,
                  connections: list[[str, str, int]],
                  sentence_first: list[str],
                  sentence_last: list[str],
                  monsters: list[int],
                  items: list[int],
                  commands: list[int],
                  additional_data: any,
                  expected_value: int,
                  sql_strings: list[str]):
    from web_application.services.itfd_creator.maps import add_node

    _init_pack(user, pack_name)

    x = add_node(user, pack_name, map_id, name, category, connections,
                 sentence_first, sentence_last, monsters, items, commands,
                 additional_data)

    assert x == expected_value

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # tests the map node data
        assert 1 == cursor.execute(sql_strings[0]).fetchone()[0]

        # test if created aa new table
        assert 1 == cursor.execute(sql_strings[1]).fetchone()[0]

        # test map_linkage
        assert 1 == cursor.execute(sql_strings[2]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[3]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[4]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[5]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[6]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[7]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[8]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[9]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[10]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[11]).fetchone()[0]

        # test monster linkage tables
        assert 1 == cursor.execute(sql_strings[12]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[13]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[14]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[15]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[16]).fetchone()[0]

        # test items Linkage tables
        assert 1 == cursor.execute(sql_strings[17]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[18]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[19]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[20]).fetchone()[0]


@pytest.mark.parametrize(
    "user, pack_name, "

    "map_id, node_id, "

    "name, "
    "category, "
    "connections, "
    "sentence_first, "
    "sentence_last, "
    "monsters, "
    "items, "
    "commands, "
    "additional_data, "

    "sql_strings",
    [
        (
            "test_user", "test_edit_node",

            1, 2,

            "Add first Node",
            1,
            [(1, "afca", 0)],
            ["hallo", "bye"],
            ["ciao"],
            [1, 2, 2],
            [0, 2, 0],
            [1, 2, 32],
            [(2, 1, "2first", 0), (2, 2, "2second", 12)],

            [
                "SELECT EXISTS(SELECT * FROM map_1 "
                "WHERE id = 2 "
                "AND name = 'Add first Node' "
                "AND category = 1 "
                "AND connections = '1;afca;0' "
                "AND sentences_first = 'hallo\nbye' "
                "AND sentences_last = 'ciao' "
                "AND monsters = '1;2;2' "
                "AND items = '0;2;0' "
                "AND commands = '1;2;32' "
                "AND additional_data = '2;1;2first;0\n2;2;2second;12')",

                "SELECT COUNT(*) = 3 FROM sqlite_master "
                "WHERE type='table' AND name LIKE '\\_map_1_%' ESCAPE '\\'",

                # test map_linkage
                "SELECT COUNT(*) = 1 FROM _map_1_1",
                "SELECT COUNT(*) = 2 FROM _map_1_2",
                "SELECT COUNT(*) = 0 FROM _map_1_3",
                "SELECT COUNT(*) = 2 FROM _map_2_1",
                "SELECT COUNT(*) = 2 FROM _map_2_2",

                "SELECT EXISTS(SELECT * FROM _map_1_1 "
                "WHERE map=1 AND node=2)",
                "SELECT EXISTS(SELECT * FROM _map_1_2 "
                "WHERE map=1 AND node=2) = 0",
                "SELECT EXISTS(SELECT * FROM _map_1_3 "
                "WHERE map=1 AND node=2) = 0",
                "SELECT EXISTS(SELECT * FROM _map_2_1 "
                "WHERE map=1 AND node=2)",
                "SELECT EXISTS(SELECT * FROM _map_2_2 "
                "WHERE map=1 AND node=2)",

                # test monster linkage tables
                "SELECT COUNT(*) = 3 FROM _monster_1",
                "SELECT COUNT(*) = 2 FROM _monster_2",
                "SELECT COUNT(*) = 0 FROM _monster_3",

                "SELECT EXISTS(SELECT count = 1 FROM _monster_1 "
                "WHERE map = 1 AND node = 2)",
                "SELECT EXISTS(SELECT count = 2 FROM _monster_2 "
                "WHERE map = 1 AND node = 2)",

                "SELECT COUNT(*) = 3 FROM _item_0_map",
                "SELECT COUNT(*) = 3 FROM _item_2_map",

                "SELECT EXISTS(SELECT count = 2 FROM _item_0_map "
                "WHERE map = 1 AND node = 2)",
                "SELECT EXISTS(SELECT count = 1  FROM _item_2_map "
                "WHERE map = 1 AND node = 2)",
            ]
        )
    ]
)
def test_edit_node(user: str,
                   pack_name: str,
                   map_id: int,
                   node_id: int,
                   name: str,
                   category: int,
                   connections: list[[str, str, int]],
                   sentence_first: list[str],
                   sentence_last: list[str],
                   monsters: list[int],
                   items: list[int],
                   commands: list[int],
                   additional_data: any,
                   sql_strings: list[str]):
    from web_application.services.itfd_creator.maps import edit_node

    _init_pack(user, pack_name)

    edit_node(user, pack_name, map_id, node_id, name, category, connections,
              sentence_first, sentence_last, monsters, items, commands,
              additional_data)

    path = f"{DATA_PATH}/users/{user}/itfd_creator/{pack_name}.db"
    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # tests the map node data
        assert 1 == cursor.execute(sql_strings[0]).fetchone()[0]

        # test if created aa new table
        assert 1 == cursor.execute(sql_strings[1]).fetchone()[0]

        # test map_linkage
        assert 1 == cursor.execute(sql_strings[2]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[3]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[4]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[5]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[6]).fetchone()[0]

        assert 1 == cursor.execute(sql_strings[7]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[8]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[9]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[10]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[11]).fetchone()[0]

        # test monster linkage tables
        assert 1 == cursor.execute(sql_strings[12]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[13]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[14]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[15]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[16]).fetchone()[0]

        # test items Linkage tables
        assert 1 == cursor.execute(sql_strings[17]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[18]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[19]).fetchone()[0]
        assert 1 == cursor.execute(sql_strings[20]).fetchone()[0]


@pytest.mark.parametrize(
    "user, pack_name, map_id, node_id",
    [
        ("test_user", "test_delete_node", 2, 2)
    ]
)
def test_delete_node(user: str,
                     pack_name: str,
                     map_id: int,
                     node_id: int):
    from web_application.services.itfd_creator.maps import delete_node

    _init_pack(user, pack_name)

    delete_node(user, pack_name, map_id, node_id)

