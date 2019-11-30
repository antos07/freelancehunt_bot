from psycopg2 import connect
from os import environ


DATABASE_URL = environ['DATABASE_URL']


def get_active_jobs():
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE is_active is True")
            return cur.fetchall()


def get_token(user_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT token FROM users WHERE user_id={user_id}")
            return cur.fetchone()


def insert_user(user_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(f"INSERT INTO users (user_id) VALUES ({user_id})")
            conn.commit()


def change_status(user_id, new_status):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active=%s WHERE user_id=%s", (new_status, user_id))
            conn.commit()


def set_active(user_id):
    change_status(user_id, True)


def set_inactive(user_id):
    change_status(user_id, False)


def get_status(user_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT is_active FROM users WHERE user_id={user_id}")
            status = cur.fetchone()
            if status is not None:
                status = status[0]
            return status


def set_token(user_id, token):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET token=%s WHERE user_id=%s", (token, user_id))
            conn.commit()


def save_status(user_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET temp_status=(SELECT is_active FROM users WHERE user_id=%s) WHERE user_id=%s",
                        (user_id, user_id))
            conn.commit()


def restore_status(user_id):
    with connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET is_active=(SELECT temp_status FROM users WHERE user_id=%s) WHERE user_id=%s",
                        (user_id, user_id))
            conn.commit()


if __name__ == "__main__":
    restore_status(357052125)
