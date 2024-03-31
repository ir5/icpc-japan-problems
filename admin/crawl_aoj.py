import os
import time

import psycopg
import requests
from ijproblems_admin.database import (
    get_postgres_url,
    insert_aoj_aceptance,
    recompute_point,
)


def get_problem_ids(conn: psycopg.Connection) -> list[int]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT problem_id FROM problems")
        problem_ids = [problem_id for problem_id, in cursor.fetchall()]
        return problem_ids


def main(conn: psycopg.Connection) -> None:
    crawl_interval_second = int(os.environ.get("CRAWL_INTERVAL_SECOND", "0"))
    if crawl_interval_second <= 0:
        print("Not crawling.")
        while True:
            time.sleep(1e9)

    problem_ids: list[int] = []

    while True:
        if len(problem_ids) == 0:
            problem_ids = get_problem_ids(conn)

        # crawl each problem
        if len(problem_ids) > 0:
            problem_id = problem_ids[-1]
            # TODO: Use pager when size limit reaches
            url = (
                "https://judgeapi.u-aizu.ac.jp/solutions/problems/"
                f"{problem_id}?size=10000"
            )
            response = requests.get(url)

            if response.status_code != 200:
                time.sleep(60)
                continue
            problem_ids.pop()
            solutions = response.json()
            users = {
                solution["userId"]: solution["submissionDate"] for solution in solutions
            }
            with conn.cursor() as cursor:
                users_recompute = []
                for aoj_userid, date_unixmilli in users.items():
                    inserted_rows = insert_aoj_aceptance(
                        cursor, aoj_userid, problem_id, date_unixmilli
                    )

                    if inserted_rows:
                        users_recompute.append(aoj_userid)

                for aoj_userid in users_recompute:
                    recompute_point(cursor, aoj_userid)
            conn.commit()

        # crawl for latest status
        time.sleep(10)
        current_problem_ids = set(get_problem_ids(conn))
        url = "https://judgeapi.u-aizu.ac.jp/solutions"
        response = requests.get(url)
        if response.status_code != 200:
            time.sleep(60)
            continue
        solutions = response.json()

        with conn.cursor() as cursor:
            for solution in solutions:
                problem_id = solution["problemId"]
                if problem_id not in current_problem_ids:
                    continue
                aoj_userid = solution["userId"]
                date_unixmilli = solution["submissionDate"]
                insert_aoj_aceptance(cursor, aoj_userid, problem_id, date_unixmilli)
                users_recompute.append(aoj_userid)
        conn.commit()

        time.sleep(crawl_interval_second)


if __name__ == "__main__":
    url = get_postgres_url()
    with psycopg.connect(url) as conn:
        main(conn)
