import os

import psycopg


def get_postgres_url() -> str:
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    hostname = "postgres"
    port = 5432
    dbname = os.environ["POSTGRES_DB"]
    url = f"postgres://{user}:{password}@{hostname}:{port}/{dbname}"
    return url


def insert_aoj_aceptance(
    cursor: psycopg.Cursor, aoj_userid: str, problem_id: int
) -> None:
    sql = (
        "INSERT INTO aoj_acceptances (aoj_userid, problem_id) "
        "VALUES (%s, %s) "
        "ON CONFLICT (aoj_userid, problem_id) DO NOTHING"
    )
    cursor.execute(sql, (aoj_userid, problem_id))
