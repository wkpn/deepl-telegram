from settings import db_name
import sqlite3


def setup_db():
    conn = sqlite3.connect(f'{db_name}')
    try:
        conn.cursor().execute('CREATE TABLE users (chat_id text, source text, target text, is_selected integer)')
        conn.commit()
        conn.close()
        print(f'Created new database {db_name}')
    except sqlite3.OperationalError:
        print(f'Loaded database {db_name}')


def add_to_db(chat_id, source, target):
    user = (chat_id, source, target, 0)
    conn = sqlite3.connect(f'{db_name}')
    conn.cursor().execute('INSERT INTO users VALUES (?,?,?,?)', user)
    conn.commit()
    conn.close()

    print(f'Added {chat_id}, {source}, {target} with False to database')


def get_from_db(chat_id, **kwargs):
    conn = sqlite3.connect(f'{db_name}')
    command = ', '.join(key for key in kwargs)
    print(f'Get command {command}')
    data = conn.cursor().execute(f"SELECT {command} FROM users WHERE chat_id='{chat_id}'").fetchone()
    print(f'Got {data} from db for {chat_id} with kwargs {kwargs}')

    return data


def update_in_db(chat_id, **kwargs):
    conn = sqlite3.connect(f'{db_name}')
    command = ', '.join(f'{key}={value}' for key, value in kwargs.items())
    print(f'Update command {command}')
    conn.cursor().execute(f"UPDATE users SET {command} WHERE chat_id='{chat_id}")
    conn.commit()
    conn.close()

    print(f'Updated {kwargs} in db for {chat_id}')
