import sqlite3


def init():
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY, password TEXT NOT NULL)")
    conn.commit()

def check_data(name: str, password: str) -> bool | None:
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT password FROM users WHERE name = ?", (name,))
    value = cursor.fetchone()
    print(value)
    if value:
        return value[0] == password
    else:
        return None


def check_if_username_forgiven(name: str) -> bool:
    """

    :param name: name that will check if its forgiven
    :return: True for is forgiven else False
    """
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM users")
    value = cursor.fetchall()
    print(value)

    value = list(map(lambda x: x[0], value))
    if value:
        value = set(value)
        if name in value:
            return True
        else:
            return False
    else:
        return False


def register_new_account(name: str, password: str):
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users(name, password) VALUES (?, ?)", (name, password))
    conn.commit()


def remove(name: str):
    conn = sqlite3.connect("data/auth.db")
    cursor = conn.cursor()

    cursor.execute(f"DELETE FROM users WHERE name = ?", (name, ))
    conn.commit()

