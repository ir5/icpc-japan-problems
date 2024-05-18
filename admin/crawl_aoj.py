import logging
import os
import time
import traceback
from logging import getLogger

import psycopg
import requests
from ijproblems_admin.database import (
    get_postgres_url,
    insert_aoj_aceptance,
    recompute_point,
)

logger = getLogger(__name__)


def get_problem_ids(conn: psycopg.Connection) -> list[int]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT problem_id FROM problems")
        problem_ids = [problem_id for problem_id, in cursor.fetchall()]
        return problem_ids


def main(conn: psycopg.Connection) -> None:
    crawl_interval_second = int(os.environ.get("CRAWL_INTERVAL_SECOND", "0"))
    if crawl_interval_second <= 0:
        logger.info("Not crawling.")
        while True:
            time.sleep(1e9)
    logger.debug(f"CRAWL_INTERVAL_SECOND={crawl_interval_second}")

    problem_ids: list[int] = []

    def crawl_problem(problem_id: int) -> bool:
        # TODO: Use pager when size limit reaches
        url = (
            "https://judgeapi.u-aizu.ac.jp/solutions/problems/"
            f"{problem_id}?size=10000"
        )
        try:
            response = requests.get(url)
        except Exception:
            logger.warning(f"crawl for {problem_id} failed")
            logger.warning(traceback.format_exc())
            return False

        if response.status_code != 200:
            return False

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

        logger.info(f"crawl for {problem_id} ok")
        logger.info(f"recomputed users = {len(users_recompute)}")
        return True

    def crawl_latest_status() -> bool:
        current_problem_ids = set(get_problem_ids(conn))
        url = "https://judgeapi.u-aizu.ac.jp/solutions"
        try:
            response = requests.get(url)
        except Exception:
            logger.warning("crawl for latest status failed")
            logger.warning(traceback.format_exc())
            return False

        if response.status_code != 200:
            return False

        solutions = response.json()

        with conn.cursor() as cursor:
            users_recompute = set()
            for solution in solutions:
                problem_id_str = solution["problemId"]
                if not problem_id_str.isdigit():
                    continue
                problem_id = int(problem_id_str)
                if problem_id not in current_problem_ids:
                    continue
                aoj_userid = solution["userId"]
                date_unixmilli = solution["submissionDate"]
                insert_aoj_aceptance(cursor, aoj_userid, problem_id, date_unixmilli)
                users_recompute.add(aoj_userid)

            for aoj_userid in users_recompute:
                recompute_point(cursor, aoj_userid)

        conn.commit()
        logger.info("crawl for latest status ok")
        logger.info(f"recomputed users = {len(users_recompute)}")
        return True

    while True:
        if len(problem_ids) == 0:
            problem_ids = get_problem_ids(conn)

        # crawl each problem
        if len(problem_ids) > 0:
            problem_id = problem_ids[-1]
            while not crawl_problem(problem_id):
                time.sleep(crawl_interval_second)

        time.sleep(crawl_interval_second)
        while not crawl_latest_status():
            time.sleep(crawl_interval_second)

        time.sleep(crawl_interval_second)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s[%(levelname)s] %(message)s", level="DEBUG")

    url = get_postgres_url()
    with psycopg.connect(url) as conn:
        try:
            main(conn)
        except Exception:
            error_details = traceback.format_exc()
            logger.critical("Aborting crawer...")
            logger.critical(error_details)
