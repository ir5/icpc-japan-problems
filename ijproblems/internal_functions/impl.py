from typing import Optional

from fastapi import Request
import psycopg

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


class InternalFunctions(InterfaceInternalFunctions):

    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def get_points(self, contest_type: int) -> list[int]:
        return POINTS[contest_type]

    def get_problems(
        self, preference: Preference, user_solved_problems: set[int]
    ) -> list[ProblemInfo]:
        contest_type = preference.contest_type
        begin = preference.level_scopes[contest_type]
        return sorted(
            [
                problem
                for problem in mock_data.problems
                if problem.contest_type == contest_type
                and problem.level >= begin
                and ((preference.ja and problem.ja) or (preference.en and problem.en))
                and not (
                    preference.hide_solved and problem.aoj_id in user_solved_problems
                )
            ],
            key=lambda problem: (problem.level, -problem.year, problem.aoj_id),
        )

    def get_problem(self, aoj_id: int) -> Optional[ProblemInfo]:
        if aoj_id in mock_data.problems_dict:
            return mock_data.problems_dict[aoj_id]
        return None

    def get_solved_user_count(self, aoj_id: int) -> int:
        return 123

    def get_problems_total_row(self, contest_type: int) -> RankingRow:
        counts = [0] * len(mock_data.points[contest_type])
        total_point = 0
        for problem in mock_data.problems:
            if problem.contest_type != contest_type:
                continue
            level = problem.level
            counts[level - 1] += 1
            total_point += mock_data.points[contest_type][level - 1]

        return RankingRow(
            aoj_userid="TOTAL",
            total_point=total_point,
            total_solved=sum(counts),
            solved_counts=counts,
        )

    def get_problem_acceptance_count(self, aoj_id: int) -> int:
        return 100

    def get_global_ranking(
        self, contest_type: int, begin: int, end: int
    ) -> list[RankingRow]:
        aoj_users = sorted(
            [aoj_user for aoj_user in mock_data.aoj_users.values()],
            key=lambda aoj_user: aoj_user.total_point[contest_type],
            reverse=True,
        )
        rows = [
            aoj_user.to_ranking_row(contest_type)
            for aoj_user in aoj_users[begin - 1 : end]
        ]
        return rows

    def get_user_count(self, contest_type: int) -> int:
        return len(mock_data.aoj_users)

    def get_github_login_info(self, request: Request) -> Optional[GitHubLoginInfo]:
        if os.environ.get("DUMMY_LOGIN"):
            return GitHubLoginInfo(github_id=123, login="dummy")
        else:
            session = request.session
            if "github_id" in session and "github_login" in session:
                return GitHubLoginInfo(
                    github_id=session["github_id"], login=session["github_login"]
                )
            else:
                return None

    def get_likes(self, github_id: int) -> set[int]:
        if github_id in like_data:
            return like_data[github_id]
        return set()

    def set_like(self, github_id: int, aoj_id: int, value: int) -> int:
        if github_id not in like_data:
            like_data[github_id] = set()

        if value:
            like_data[github_id].add(aoj_id)
        else:
            like_data[github_id].discard(aoj_id)
        return mock_data.problems_dict[aoj_id].likes + value

    def get_user_local_ranking(
        self, contest_type: int, aoj_userids: list[str]
    ) -> list[RankingRow]:
        rows: list[RankingRow] = []
        for aoj_userid in aoj_userids:
            if aoj_userid not in mock_data.aoj_users:
                empty_row = RankingRow(
                    aoj_userid=aoj_userid,
                    total_point=0,
                    total_solved=0,
                    solved_counts=[0] * len(mock_data.points[contest_type]),
                )
                rows.append(empty_row)
            else:
                user = mock_data.aoj_users[aoj_userid]
                rows.append(user.to_ranking_row(contest_type))
            rows = sorted(
                rows, key=lambda row: (row.total_point, row.aoj_userid), reverse=True
            )
        return rows

    def get_user_solved_problems(self, aoj_userid: str) -> set[int]:
        if aoj_userid in mock_data.aoj_users:
            user = mock_data.aoj_users[aoj_userid]
            return user.aoj_ids
        return set()
