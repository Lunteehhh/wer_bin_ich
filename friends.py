import sqlite3

from typing import Optional

try:
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()
    friends_count = cursor.execute("SELECT COUNT(*) FROM friends").fetchone()[0]
except sqlite3.OperationalError:
    friends_count = 0


def init():
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS friends(name TEXT PRIMARY KEY, friends_page TEXT NOT NULL)")
    conn.commit()


def search(name: str) -> list | None:
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM friends WHERE name LIKE '%{name}%'")
    results = cursor.fetchall()
    return results


def get_friends_page(name: str) -> any:
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT friends_page FROM friends WHERE name IS '{name}'")
    friends_page = cursor.fetchone()
    return friends_page


def add(name: str):
    global friends_count
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO friends(name, friends_page) VALUES (\"{name}\", "
                   f"\"/friends-page?name={name}\")")
    conn.commit()

    friends_count += 1


def remove(name: str):
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM friends WHERE name = ?", (name,))
    conn.commit()


def update_friends_page(name: str, friends_page: Optional[str] = None):
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    if friends_page:
        cursor.execute(f"UPDATE friends SET friends_page = \"{friends_page}\" WHERE name = \"{name}\"")
    else:
        cursor.execute(f"UPDATE friends SET friends_page = \"/friends-page?name={name}\" WHERE name = \"{name}\"")
    conn.commit()

if __name__ == "__main__":
    init()
