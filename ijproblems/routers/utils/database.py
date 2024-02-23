import os

from psycopg_pool import ConnectionPool


def get_postgres_url() -> str:
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    hostname = "postgres"
    port = 5432
    dbname = os.environ["POSTGRES_DB"]
    url = f"postgres://{user}:{password}@{hostname}:{port}/{dbname}"
    return url


_pool = ConnectionPool(get_postgres_url())


def get_db_conn():
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)
