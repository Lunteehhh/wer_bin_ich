import os
import sqlite3
import pytest

from web_application.core.config import DATA_PATH

from web_application.services.itfd_creator.maps import (
    Node,
    _convert_connections_to_string,
    _convert_entrances_to_string,
    _convert_string_to_connections,
    _convert_string_to_entrances,
    _node_from_db
)


def init_test_db(pack: str,
                 user: str):
    path = f"../../../{DATA_PATH}/{pack}_{user}.db"
    print(os.path.abspath(path))

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        with open("../../sql/init_itfd_creator_test_pack.sql", "r") as file:
            sql_string = file.read()

        cursor.execute(sql_string)

        conn.commit()



def delete_test_db(pack: str,
                   user: str):
    path = f"{DATA_PATH}/{pack}/{user}.db"

    os.remove(path)

init_test_db("hall", "new")
input()
delete_test_db("hall", "new")

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
    "user, pack_name",
    [

    ]
)
def test_add_map(user: str, pack_name: str):
    pass
