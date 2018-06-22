from settings import db_name
import sqlite3


def setup_db():
    conn = sqlite3.connect(f'{db_name}')
    conn.cursor().execute('''CREATE TABLE IF NOT EXISTS users 
                                 (chat_id integer unique, source text, target text, lock text)''')
    conn.commit()
    conn.close()


def add_user_to_db(chat_id, source, target):
    conn = sqlite3.connect(f'{db_name}')

    try:
        conn.cursor().execute('INSERT INTO users VALUES (?,?,?,?)', (chat_id, source, target, 0))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:  # it means user is already in db
        pass


def get_from_db(chat_id, **kwargs):
    values = ', '.join(key for key in kwargs)

    conn = sqlite3.connect(f'{db_name}')
    data = conn.cursor().execute(f"SELECT {values} FROM users WHERE chat_id={chat_id}").fetchone()

    if len(data) == 1:
        return data[0]
    return data


def update_in_db(chat_id, **kwargs):
    key_values = ', '.join(f"{key}='{value}'" for key, value in kwargs.items())

    conn = sqlite3.connect(f'{db_name}')
    conn.cursor().execute(f'UPDATE users SET {key_values} WHERE chat_id={chat_id}')
    conn.commit()
    conn.close()
