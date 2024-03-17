import os
import json

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
) -> int:
    res = cursor.execute(
        "INSERT INTO aoj_acceptances (aoj_userid, problem_id) "
        "VALUES (%(aoj_userid)s, %(problem_id)s) "
        "ON CONFLICT (aoj_userid, problem_id) DO NOTHING",
        {
            "aoj_userid": aoj_userid,
            "problem_id": problem_id
        }
    )
    return res.rowcount


POINTS = [
    [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330],
    [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900],
]


def recompute_point(
    cursor: psycopg.Cursor, aoj_userid: str
):
    res = cursor.execute(
        "SELECT P.level AS level, P.contest_type AS contest_type, COUNT(*) AS count "
        "FROM aoj_acceptances AS A "
        "JOIN problems AS P ON A.problem_id=P.problem_id "
        "WHERE A.aoj_userid=%(aoj_userid)s "
        "GROUP BY (P.level, P.contest_type)",
        {
            "aoj_userid": aoj_userid
        }
    ).fetchall()

    for contest_type in range(2):
        solved = [0] * len(POINTS[contest_type])
        for level, contest_type_, count in res:
            if contest_type_ == contest_type:
                solved[level - 1] = count
        total = sum(s * p for s, p in zip(solved, POINTS[contest_type]))
        if total == 0:
            continue
        counts = json.dumps(solved)

        print(aoj_userid, total, contest_type, counts)

        cursor.execute(
            "INSERT INTO user_points "
            "(aoj_userid, contest_type, total, counts_per_levels) "
            "VALUES (%(aoj_userid)s, %(contest_type)s, %(total)s, %(counts)s)"
            "ON CONFLICT (aoj_userid, contest_type) DO UPDATE "
            "SET total = EXCLUDED.total, "
            "counts_per_levels = EXCLUDED.counts_per_levels",
            {
                "aoj_userid": aoj_userid,
                "total": total,
                "contest_type": contest_type,
                "counts": counts
            }
        )
