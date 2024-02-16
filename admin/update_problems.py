"""
From a spreadsheet, update the current problem table
and recalculate the points if necessary.
"""

import argparse
import csv
import dataclasses
import json
import os
from dataclasses import dataclass
from io import StringIO
from typing import Any

import psycopg
import requests
from psycopg.rows import class_row


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
    en: int
    ja: int
    inherited_likes: int
    meta: str

    def __post_init__(self) -> None:
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            setattr(self, field.name, field.type(value))


def perf_to_level(perf: int, contest_type: int) -> int:
    if contest_type == 0:
        uppers = [7, 17, 27, 37, 47, 57, 67, 77, 87, 97, 100]
    else:
        uppers = [7, 17, 27, 37, 47, 57, 67, 77, 100]

    for level, upper in enumerate(uppers, 1):
        if perf <= upper:
            return level
    raise RuntimeError("perf is out of bound: {perf}")


def main(conn: psycopg.Connection) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sheet_name")
    args = parser.parse_args()

    # retrieve all problems in the table

    with conn.cursor(row_factory=class_row(ProblemRow)) as cursor:
        problems = cursor.execute(
            "SELECT problem_id, name, contest_type,"
            "level, org, year, used_in, slot, en, ja, "
            "inherited_likes, meta FROM problems"
        ).fetchall()
    problems_dict = {problem.problem_id: problem for problem in problems}

    sheet_id = os.environ.get("ADMIN_SHEET_ID", "")
    sheet_name = args.sheet_name
    url = (
        "https://docs.google.com/spreadsheets/d/"
        f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError(f"response: {response}")

    need_recalculation = False
    create_problems: list[ProblemRow] = []
    update_problems: list[ProblemRow] = []

    for row in csv.DictReader(StringIO(response.text)):
        if row["problem_id"] == "":
            continue

        meta: dict[str, Any] = {}
        for key, castto in (
            ("solved_teams", int),
            ("participated_teams", int),
            ("authors", str),
        ):
            if key in row and row[key] != "":
                meta[key] = castto(row[key])

        editorials = []
        for key in ("official_editorial_en", "official_editorial_ja"):
            if key in row and row[key] != "":
                editorials.append(
                    {
                        "en": key.endswith("en"),
                        "ja": key.endswith("ja"),
                        "url": row[key],
                    }
                )

        for key in ("user_editorial1", "user_editorial2"):
            if key in row and row[key] != "":
                editorials.append({"en": False, "ja": True, "url": row[key]})
        meta["editorials"] = editorials
        row["meta"] = json.dumps(meta, sort_keys=True)

        if len(row["inherited_likes"]) == 0:
            row["inherited_likes"] = 0
        perf = int(row["perf_final"])
        contest_type = int(row["contest_type"])
        level = perf_to_level(perf, contest_type)
        row["level"] = level

        problem = ProblemRow(
            **{key: row[key] for key in ProblemRow.__match_args__}  # type: ignore
        )
        problem_id = problem.problem_id

        if problem_id in problems_dict:
            current = problems_dict[problem_id]
            if current == problem:
                continue
            if (
                current.contest_type != problem.contest_type
                or current.level != problem.level
            ):
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
            print(dataclasses.asdict(problem))
            cursor.execute(
                (
                    "UPDATE problems "
                    "SET "
                    "name=%(name)s, "
                    "contest_type=%(contest_type)s, "
                    "level=%(level)s, "
                    "org=%(org)s, "
                    "year=%(year)s, "
                    "used_in=%(used_in)s, "
                    "slot=%(slot)s, "
                    "ja=%(ja)s, "
                    "en=%(en)s, "
                    "inherited_likes=%(inherited_likes)s, "
                    "meta=%(meta)s "
                    "WHERE problem_id=%(problem_id)s;"
                ),
                dataclasses.asdict(problem),
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
                    "year, "
                    "used_in, "
                    "slot, "
                    "ja, "
                    "en, "
                    "inherited_likes, "
                    "meta) "
                    "VALUES "
                    "(%(problem_id)s, "
                    "%(name)s, "
                    "%(contest_type)s, "
                    "%(level)s, "
                    "%(org)s, "
                    "%(year)s, "
                    "%(used_in)s, "
                    "%(slot)s, "
                    "%(ja)s, "
                    "%(en)s, "
                    "%(inherited_likes)s, "
                    "%(meta)s)"
                ),
                dataclasses.asdict(problem),
            )


if __name__ == "__main__":
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    hostname = "postgres"
    port = 5432
    dbname = os.environ["POSTGRES_DB"]
    url = f"postgres://{user}:{password}@{hostname}:{port}/{dbname}"

    with psycopg.connect(url) as conn:
        main(conn)
