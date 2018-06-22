from settings import db_name
import logging
import sqlite3


def setup_db():
    conn = sqlite3.connect(f'{db_name}')
    conn.cursor().execute('CREATE TABLE users (chat_id text, source text, target text, is_selected boolean)')
    conn.commit()
    conn.close()

    print('Database created')


def add_to_db(chat_id, source, target):
    user = (chat_id, source, target, False)
    conn = sqlite3.connect(f'{db_name}')
    conn.cursor().execute('INSERT INTO users VALUES (?,?,?,?)', user)
    conn.commit()
    conn.close()

    print(f'Added {chat_id}, {source}, {target} with False to database')


def get_from_db(chat_id, **kwargs):
    conn = sqlite3.connect(f'{db_name}')
    command = ', '.join(key for key in kwargs)

    data = conn.cursor().execute(f"SELECT {command} FROM users WHERE chat_id='{chat_id}'").fetchone()
    print(f'Got {**kwargs} from db for {chat_id}')

    return data


def update_in_db(chat_id, **kwargs):
    conn = sqlite3.connect(f'{db_name}')
    command = ', '.join(f'{key}={value}' for key, value in kwargs.items())

    conn.cursor().execute(f"UPDATE users SET {command} WHERE chat_id='{chat_id}")
    conn.commit()
    conn.close()

    print(f'Updated {**kwargs} in db for {chat_id}')
