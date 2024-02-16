import time

import psycopg
import requests

from ijproblems_admin.database import get_postgres_url, insert_aoj_aceptance


def get_problem_ids(conn: psycopg.Connection) -> list[int]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT problem_id FROM problems")
        problem_ids = [problem_id for problem_id, in cursor.fetchall()]
        return problem_ids


def main(conn):
    craw_interval_second = 60

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
                time.sleep(5)
                continue
            problem_ids.pop()
            solutions = response.json()
            users = set(solution["userId"] for solution in solutions)
            with conn.cursor() as cursor:
                for aoj_userid in users:
                    insert_aoj_aceptance(cursor, aoj_userid, problem_id)
            conn.commit()

        # crawl for latest status
        time.sleep(5)
        current_problem_ids = set(get_problem_ids(conn))
        url = (
            "https://judgeapi.u-aizu.ac.jp/solutions"
        )
        response = requests.get(url)
        if response.status_code != 200:
            time.sleep(5)
            continue
        solutions = response.json()

        with conn.cursor() as cursor:
            for solution in solutions:
                problem_id = solution["problemId"]
                if problem_id not in current_problem_ids:
                    continue
                aoj_userid = solution["userId"]
                insert_aoj_aceptance(cursor, aoj_userid, problem_id)
        conn.commit()

        time.sleep(craw_interval_second)


if __name__ == "__main__":
    url = get_postgres_url()
    with psycopg.connect(url) as conn:
        main(conn)
