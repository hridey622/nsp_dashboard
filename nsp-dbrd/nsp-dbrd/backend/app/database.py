from flask import g
import psycopg2
from psycopg2.extras import DictCursor
from app.config import DB_CONFIGS

def get_db_connection():
    if 'db_conn' not in g:
        config = DB_CONFIGS['nsp_fresh']
        g.db_conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname'],
            cursor_factory=DictCursor
        )
    return g.db_conn

def close_db_connection(e=None):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()