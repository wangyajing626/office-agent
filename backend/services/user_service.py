import pymysql
import bcrypt
from core.database import get_db_connection

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def register_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, None, "用户名已存在"

        hashed = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return True, user_id, "注册成功"

    except pymysql.Error as e:
        conn.rollback()
        return False, None, f"数据库错误: {str(e)}"

    finally:
        cursor.close()
        conn.close()

def login_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, username, password FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            return False, None, "用户名或密码错误"

        if not verify_password(password, user["password"]):
            return False, None, "用户名或密码错误"

        return True, {"id": user["id"], "username": user["username"]}, "登录成功"

    except pymysql.Error as e:
        return False, None, f"数据库错误: {str(e)}"

    finally:
        cursor.close()
        conn.close()