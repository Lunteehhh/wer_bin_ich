import sqlite3


def init():
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS friends(name TEXT PRIMARY KEY, friends_page_href TEXT NOT NULL)")
    conn.commit()


def search(name: str) -> list | None:
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM friends WHERE name LIKE '%{name}%'")
    results = cursor.fetchall()
    return results


def add(name: str):
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO friends(name, friends_page_href) VALUES ({name}, /data/friends_pages/{name}.html)")
    conn.commit()


def remove(name: str):
    conn = sqlite3.connect("data/friends.db")
    cursor = conn.cursor()

    cursor.execute(f"DELETE * FROM friends WHERE name LIKE '{name}'")

if __name__ == "__main__":
    init_database()