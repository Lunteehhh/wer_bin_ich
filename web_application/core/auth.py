import os
import shutil

from fastapi import Request
from jose import JWTError, jwt
from pysqlcipher3 import dbapi2 as sqlite


from datetime import datetime, timezone

from web_application.core.config import PRAGMA_KEY, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE


def init():
    """
    Initialize the auth databank with the PRAGMA_KEY of the config.py
    """
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "    name TEXT PRIMARY KEY, "
                   "    password TEXT NOT NULL)")
    conn.commit()


def check_data(name: str, password: str) -> bool | None:
    """
    checks if the login params correct

    :param name: name of the user
    :param password: of the user
    :return: None if not user was found, True for passsword correct else False
    """
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute(f"SELECT password FROM users WHERE name = ?", (name,))
    value = cursor.fetchone()

    if value:
        return value[0] == password
    else:
        return None


def check_if_username_forgiven(name: str) -> bool:
    """
    checks th auth.db if a user have the name

    :param name: name that will check if its forgiven
    :return: True if name forgiven else False
    """
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute(f"SELECT name FROM users")
    value = cursor.fetchall()

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
    """
    Register a new and insert the name and password.

    :param name: Name of the new user
    :param password: Password of the new user
    """
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute("INSERT INTO users(name, password) VALUES (?, ?)",
                   (name, password))
    conn.commit()

    os.makedirs(f"data/users/{name}")
    os.makedirs(f"data/users/{name}/itfd_creator")


def remove(name: str):
    """
    Deletes a user entry in the auth.db.

    :param name: Name of the user
    """
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute(f"DELETE FROM users WHERE name = ?", (name, ))
    conn.commit()

    shutil.rmtree("data/users/lunte")


def create_token(data: dict):
    """
    Creates the JWToken and adds the guilty time

    :param data: dict of the user dsta
    """
    data["exp"] = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE

    encoded_jwt = jwt.encode(data, SECRET_KEY, ALGORITHM)

    return encoded_jwt


async def check_access_token(request: Request):
    """
    checks if the JWToken if

    :param request:
    """
    token = request.cookies.get("access_token")
    if not token:
        return {"error": 1}

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_name = payload.get("sub")
        if user_name is None:
            return {"error": 2}

    except JWTError:
        return {"error": 3}

    if not check_if_username_forgiven(user_name):
        return {"error": 4}

    return {
        "error": 0,
        "user_name": user_name
    }