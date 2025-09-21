import sqlite3
import pytest


@pytest.fixture
def temp_pack(tmp_path):
    db_path = tmp_path / "test_pack.db"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS maps("
                       "    id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "    name TEXT)")

        conn.commit()

        yield str(db_path)

        conn.close()
