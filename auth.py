from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from pysqlcipher3 import dbapi2 as sqlite


from datetime import timedelta, datetime, timezone

from config import PRAGMA_KEY, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE


def init():
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')


    cursor.execute("CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY, password TEXT NOT NULL)")
    conn.commit()


def check_data(name: str, password: str) -> bool | None:
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

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
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

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
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute("INSERT INTO users(name, password) VALUES (?, ?)", (name, password))
    conn.commit()


def remove(name: str):
    conn = sqlite.connect("data/auth.db")
    cursor = conn.cursor()
    cursor.execute(f'PRAGMA key = "{PRAGMA_KEY}"')

    cursor.execute(f"DELETE FROM users WHERE name = ?", (name, ))
    conn.commit()


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def check_access_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nicht eingeloggt.",
        )

    try:
        # 2) Token decodieren
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 3) Username aus Payload holen
        user_name = payload.get("sub")
        if user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ungültig.",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token konnte nicht verifiziert werden.",
        )

    if not check_if_username_forgiven(user_name):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Benutzer nicht gefunden.",
        )

    return {"user_name": user_name}