import dataclasses
import json
from dataclasses import asdict, dataclass
from typing import Optional

import psycopg
from fastapi import Request
from psycopg.rows import class_row

from ijproblems.internal_functions.interface import (
    Editorial,
    GitHubLoginInfo,
    InterfaceInternalFunctions,
    Preference,
    ProblemInfo,
    RankingRow,
)
from ijproblems.internal_functions.points import POINTS


@dataclass
class ProblemTableRow:
    contest_type: int
    name: str
    level: int
    aoj_id: int
    org: str
    year: int
    en: int
    ja: int
    inherited_likes: int
    likes_github: int

    def __post_init__(self) -> None:
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            setattr(self, field.name, field.type(value))


def parse_meta(problem_info: ProblemInfo) -> None:
    meta = problem_info.meta
    meta_obj = json.loads(meta)

    for key in ("solved_teams", "participated_teams", "authors"):
        if key in meta_obj:
            setattr(problem_info, key, meta_obj[key])

    problem_info.editorials = [
        Editorial(**editorial) for editorial in meta_obj["editorials"]
    ]


class ImplInternalFunctions(InterfaceInternalFunctions):

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def get_points(self, contest_type: int) -> list[int]:
        return POINTS[contest_type]

    def get_problems(
        self, preference: Preference, user_solved_problems: set[int]
    ) -> list[ProblemInfo]:
        # NOTE: meta info is ignored
        with self.conn.cursor(row_factory=class_row(ProblemTableRow)) as cursor:
            problems_row = cursor.execute(
                "SELECT P.contest_type AS contest_type,"
                "P.name AS name,"
                "P.level AS level,"
                "P.problem_id AS aoj_id,"
                "P.org AS org,"
                "P.year AS year,"
                "P.en AS en,"
                "P.ja AS ja,"
                "P.inherited_likes AS inherited_likes,"
                "COUNT(L.github_id) AS likes_github "
                "FROM problems AS P "
                "LEFT JOIN likes AS L ON P.problem_id = L.problem_id "
                "WHERE P.contest_type=%(contest_type)s "
                "AND P.level>=%(level_scope)s "
                "GROUP BY P.problem_id",
                {
                    "contest_type": preference.contest_type,
                    "level_scope": preference.level_scopes[preference.contest_type],
                },
            ).fetchall()

        def to_problem_info(row: ProblemTableRow) -> ProblemInfo:
            likes = row.likes_github + row.inherited_likes
            obj = asdict(row)
            del obj["likes_github"]
            return ProblemInfo(
                **obj,
                likes=likes,
            )

        return sorted(
            [
                to_problem_info(problem)
                for problem in problems_row
                if ((preference.ja and problem.ja) or (preference.en and problem.en))
                and not (
                    preference.hide_solved and problem.aoj_id in user_solved_problems
                )
            ],
            key=lambda problem: (problem.level, -problem.year, problem.aoj_id),
        )

    def get_problem(self, aoj_id: int) -> Optional[ProblemInfo]:
        with self.conn.cursor(row_factory=class_row(ProblemInfo)) as cursor:
            res = cursor.execute(
                "SELECT contest_type,"
                "name,"
                "level,"
                "P.problem_id AS aoj_id,"
                "org,"
                "year,"
                "used_in,"
                "slot,"
                "en,"
                "ja,"
                "inherited_likes,"
                "meta,"
                "COUNT(L.github_id) AS likes "
                "FROM problems AS P "
                "LEFT JOIN likes AS L ON P.problem_id = L.problem_id "
                "WHERE P.problem_id=%(problem_id)s "
                "GROUP BY P.problem_id",
                {"problem_id": aoj_id},
            ).fetchone()
        if res is None:
            return None
        parse_meta(res)
        res.likes += res.inherited_likes
        return res

    def get_solved_user_count(self, aoj_id: int) -> int:
        res = self.conn.execute(
            "SELECT COUNT(*) AS count "
            "FROM aoj_acceptances "
            "WHERE problem_id=%(problem_id)s ",
            {
                "problem_id": aoj_id,
            },
        ).fetchone()

        if res is None:
            raise Exception("counting failed")

        return res[0]

    def get_problems_total_row(self, contest_type: int) -> RankingRow:
        level_counts = self.conn.execute(
            "SELECT level, COUNT(*) AS count "
            "FROM problems "
            "WHERE contest_type=%(contest_type)s "
            "GROUP BY level ",
            {
                "contest_type": contest_type,
            },
        )
        counts = [count for _level, count in sorted(level_counts)]
        total_point = sum(
            point * count for point, count in zip(POINTS[contest_type], counts)
        )

        return RankingRow(
            aoj_userid="TOTAL",
            total_point=total_point,
            total_solved=sum(counts),
            solved_counts=counts,
        )

    def get_global_ranking(
        self, contest_type: int, begin: int, end: int
    ) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_count(self, contest_type: int) -> int:
        # WIP
        self.conn.execute(
            "SELECT COUNT(*) AS count "
            "FROM problems "
            "WHERE contest_type=%(contest_type)s "
            "GROUP BY level ",
            {
                "contest_type": contest_type,
            },
        )

    def get_github_login_info(self, request: Request) -> Optional[GitHubLoginInfo]:
        session = request.session
        if "github_id" in session and "github_login" in session:
            return GitHubLoginInfo(
                github_id=session["github_id"], login=session["github_login"]
            )
        else:
            return None

    def get_likes(self, github_id: int) -> set[int]:
        res = self.conn.execute(
            "SELECT problem_id " "FROM likes " "WHERE github_id=%(github_id)s ",
            {
                "github_id": github_id,
            },
        ).fetchall()
        return set(entry for entry, in res)

    def set_like(self, github_id: int, aoj_id: int, value: int) -> int:
        inherited_likes_res = self.conn.execute(
            "SELECT inherited_likes FROM problems WHERE problem_id=%(problem_id)s",
            {"problem_id": aoj_id},
        ).fetchone()

        if inherited_likes_res is None:
            raise Exception(f"invalid aoj_id: {aoj_id}")

        (inherited_likes,) = inherited_likes_res

        if value == 0:
            self.conn.execute(
                "DELETE FROM likes "
                "WHERE github_id=%(github_id)s AND problem_id=%(problem_id)s ",
                {
                    "github_id": github_id,
                    "problem_id": aoj_id,
                },
            )
        elif value == 1:
            self.conn.execute(
                "INSERT INTO likes (github_id, problem_id) "
                "VALUES (%(github_id)s, %(problem_id)s) "
                "ON CONFLICT (github_id, problem_id) DO NOTHING",
                {
                    "github_id": github_id,
                    "problem_id": aoj_id,
                },
            )
        else:
            raise NotImplementedError

        self.conn.commit()
        likes_res = self.conn.execute(
            "SELECT COUNT(*) AS count " "FROM likes WHERE problem_id=%(problem_id)s",
            {
                "problem_id": aoj_id,
            },
        ).fetchone()

        if likes_res is None:
            raise Exception("database error")

        (likes,) = likes_res

        return inherited_likes + likes

    def get_user_local_ranking(
        self, contest_type: int, aoj_userids: list[str]
    ) -> list[RankingRow]:
        return []

    def get_user_solved_problems(self, aoj_userid: str) -> set[int]:
        res = self.conn.execute(
            "SELECT problem_id FROM aoj_acceptances " "WHERE aoj_userid=%(aoj_userid)s",
            {"aoj_userid": aoj_userid},
        ).fetchall()

        return set(entry for entry, in res)
