"""
From a spreadsheet, update the current problem table
and recalculate the points if necessary.
"""

import argparse
import csv
import dataclass
import json
import os
from typing import Any

import psycopg
import requests


@dataclass
class ProblemRow:
    problem_id: int
    name: str
    contest_type: int
    level: int
    org: str
    year: int
    used_in: str
    slot: str
    en: bool
    ja: bool
    inherited_likes: int = 0
    meta: str


def main(conn: psycopg.Connection) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet_name")
    args = parser.parse()

    # retrieve all problems in the table

    with conn.cursor(row_factory=ProblemRow) as cursor:
        problems = cursor.execute(
            "SELECT (problem_id, name, contest_type,"
            "level, org, used_in, slot, en, ja, inherited_likes, meta) FROM problems"
        ).fetchall()
    problems_dict = {problem.problem_id: problem for problem in problems}

    sheet_id = os.environ("ADMIN_SHEET_ID", "")
    sheet_name = args.sheet_name
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    response = requests.get(url)

    if response.code != 200:
        raise RuntimeError(f"response: {response}")

    need_recalculation = False
    create_problems: ProblemRow = []
    update_problems: ProblemRow = []

    for row in csv.DictReader(response.text):
        if row["problem_id"] == "":
            continue

        meta: dict[str, Any] = {}
        for key, castto in (("solved_teams", int), ("participated_teams", int), ("authors", str)):
            if key in row and row[key] != "":
                meta[key] = castto(row[key])

        for key in ("official_editorial_en", "official_editorial_ja"):
            if key in row and row[key] != "":
                meta[key] = {
                    "en": key.endswith("en"),
                    "ja": key.endswith("ja"),
                    "url": row[key]
                }

        for key in ("user_editorial1", "user_editorial2"):
            if key in row:
                meta[key] = {
                    "en": False,
                    "ja": True,
                    "url": row[key]
                }
        row["meta"] = json.dumps(meta, sort_keys=True)

        problem = ProblemRow(**{key: row[key] for key in ProblemRow.__match_args__})
        problem_id = problem.problem_id

        if problem_id in problems_dict:
            current = problems_dict[problem_id]
            if current == problem:
                continue
            if current.contest_type != problem.contest_type or current.level != problem.level:
                need_recalculation = True
            update_problems.append(problem)
        else:
            create_problems.append(problem)

    if len(update_problems) == 0 and len(create_problems) == 0:
        print("No updates found")
        return

    if update_problems:
        print("Problems to update:")
        for problem in update_problems:
            print(f"* AOJ {problem.problem_id} (level={problem.level}) {problem.name}")
    if create_problems:
        print("Problems to newly create:")
        for problem in create_problems:
            print(f"* AOJ {problem.problem_id} (level={problem.level}) {problem.name}")
    if need_recalculation:
        print("Recalculation of points will be performed!!!")

    print()
    print("Continue? [Y] to proceed")

    if input().rstrip() != "Y":
        return

    with conn.cursor() as cursor:
        for problem in update_problems:
            cursor.execute(
                (
                    "UPDATE problems"
                    "SET "
                    "name=%(name), "
                    "contest_type=%(contest_type), "
                    "level=%(level), "
                    "org=%(org), "
                    "used_in=%(used_in), "
                    "slot=%(slot), "
                    "ja=%(ja), "
                    "en=%(en), "
                    "inherited_likes=%(inherited_likes), "
                    "meta=%(meta), "
                    "WHERE problem_id=%(problem_id);"
                ),
                dataclass.asdict(problem)
            )

        for problem in create_problems:
            cursor.execute(
                (
                    "INSERT INTO problems"
                    "(problem_id, "
                    "name, "
                    "contest_type, "
                    "level, "
                    "org, "
                    "used_in, "
                    "slot, "
                    "ja, "
                    "en, "
                    "inherited_likes, "
                    "meta) "
                    "VALUES "
                    "(%(problem_id), "
                    "%(name), "
                    "%(contest_type), "
                    "%(level), "
                    "%(org), "
                    "%(used_in), "
                    "%(slot), "
                    "%(ja), "
                    "%(en), "
                    "%(inherited_likes), "
                    "%(meta)"
                ),
                dataclass.asdict(problem)
            )


if __name__ == "__main__":
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    hostname = "postgres"
    port = 5432
    dbname = os.environ["POSTGRES_DB"]
    url = "postgres://user:password@hostname:port/dbname"

    with psycopg.connect(url) as conn:
        main(conn)
