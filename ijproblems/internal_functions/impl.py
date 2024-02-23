from typing import Optional

import psycopg
from fastapi import Request

from ijproblems.internal_functions.interface import (
    AOJUser,
    Editorial,
    GitHubLoginInfo,
    InterfaceInternalFunctions,
    Preference,
    ProblemInfo,
    RankingRow,
)
from ijproblems.internal_functions.points import POINTS


class ImplInternalFunctions(InterfaceInternalFunctions):

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def get_points(self, contest_type: int) -> list[int]:
        return POINTS[contest_type]

    def get_problems(
        self, preference: Preference, user_solved_problems: set[int]
    ) -> list[ProblemInfo]:
        raise NotImplementedError

    def get_problem(self, aoj_id: int) -> Optional[ProblemInfo]:
        raise NotImplementedError

    def get_solved_user_count(self, aoj_id: int) -> int:
        raise NotImplementedError

    def get_problems_total_row(self, contest_type: int) -> RankingRow:
        raise NotImplementedError

    def get_problem_acceptance_count(self, aoj_id: int) -> int:
        raise NotImplementedError

    def get_global_ranking(
        self, contest_type: int, begin: int, end: int
    ) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_count(self, contest_type: int) -> int:
        raise NotImplementedError

    def get_github_login_info(self, request: Request) -> Optional[GitHubLoginInfo]:
        session = request.session
        if "github_id" in session and "github_login" in session:
            return GitHubLoginInfo(
                github_id=session["github_id"], login=session["github_login"]
            )
        else:
            return None

    def get_likes(self, github_id: int) -> set[int]:
        raise NotImplementedError

    def set_like(self, github_id: int, aoj_id: int, value: int) -> int:
        raise NotImplementedError

    def get_user_local_ranking(
        self, contest_type: int, aoj_userids: list[str]
    ) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_solved_problems(self, aoj_userid: str) -> set[int]:
        raise NotImplementedError
