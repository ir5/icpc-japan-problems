import os
import random
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Request

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
class AOJUser:
    aoj_userid: str
    total_point: list[int]
    total_solved: list[int]
    solved_counts: list[list[int]]
    aoj_ids: set[int]

    @classmethod
    def from_aoj_ids(
        cls,
        aoj_userid: str,
        aoj_ids: set[int],
        problems: dict[int, ProblemInfo],
        points: list[list[int]],
    ) -> "AOJUser":
        n = len(points)
        total_point = [0] * n
        total_solved = [0] * n
        solved_counts = [[0] * len(points_element) for points_element in points]

        for aoj_id in aoj_ids:
            problem = problems[aoj_id]
            contest_type = problem.contest_type
            level = problem.level
            total_point[contest_type] += points[contest_type][level - 1]
            total_solved[contest_type] += 1
            solved_counts[contest_type][level - 1] += 1

        return AOJUser(
            aoj_userid=aoj_userid,
            total_point=total_point,
            total_solved=total_solved,
            solved_counts=solved_counts,
            aoj_ids=aoj_ids,
        )

    def to_ranking_row(self, contest_type: int) -> RankingRow:
        return RankingRow(
            aoj_userid=self.aoj_userid,
            total_point=self.total_point[contest_type],
            total_solved=self.total_solved[contest_type],
            solved_counts=self.solved_counts[contest_type],
        )


class MockData:
    def __init__(self) -> None:
        self.points = POINTS

        problems: list[ProblemInfo] = []
        for level, _ in enumerate(self.points[0], 1):
            for _n in range(20 - level):
                dummy_id = 1500 + len(problems)
                likes = random.randint(0, level)
                if random.randint(0, 1) == 0:
                    org = "Official"
                    used_in = ""
                else:
                    org = "JAG"
                    used_in = ""
                problems.append(
                    ProblemInfo(
                        contest_type=0,
                        name=f"Mock Domestic Problem {dummy_id}",
                        level=level,
                        aoj_id=dummy_id,
                        org=org,
                        year=random.randint(2010, 2024),
                        used_in=used_in,
                        slot="ABCDEFGH"[random.randint(0, 7)],
                        en=True,
                        ja=True,
                        likes=likes,
                        inherited_likes=0,
                        editorials=[],
                        participated_teams=300,
                        solved_teams=120,
                        authors="someone",
                    )
                )

        for level, _ in enumerate(self.points[1], 1):
            for _n in range(40 - level):
                dummy_id = 2000 + len(problems)
                ja = False
                en = True
                if random.randint(0, 4) == 0:
                    ja = True
                    en = False
                likes = random.randint(0, level)
                if random.randint(0, 2) == 0:
                    org = "Official"
                    used_in = ""
                else:
                    org = "JAG"
                    used_in = "Practice"
                url = (
                    "https://jag-icpc.org/?2014%2FPractice%2F%E6%98%A5%E3%82"
                    + "%B3%E3%83%B3%E3%83%86%E3%82%B9%E3%83%88%2F%E8%AC%9B%E8%A9%95"
                )
                problems.append(
                    ProblemInfo(
                        contest_type=1,
                        name=f"Mock Regional Problem {dummy_id}",
                        level=level,
                        aoj_id=dummy_id,
                        org=org,
                        year=random.randint(2010, 2024),
                        used_in=used_in,
                        slot="ABCDEFGHIJK"[random.randint(0, 10)],
                        en=en,
                        ja=ja,
                        likes=likes,
                        inherited_likes=0,
                        editorials=[
                            Editorial(
                                official=True,
                                en=True,
                                ja=False,
                                url=url,
                            )
                        ],
                        participated_teams=45,
                        solved_teams=14,
                        authors="someone",
                    )
                )
        self.problems = problems

        self.problems_dict = {problem.aoj_id: problem for problem in self.problems}
        n_users = 2000
        self.aoj_users: dict[str, AOJUser] = {}
        for i in range(n_users):
            aoj_userid = f"user{i}"
            aoj_ids = set()
            for problem in self.problems:
                if random.randint(0, 3) == 0:
                    aoj_ids.add(problem.aoj_id)

            aoj_user = AOJUser.from_aoj_ids(
                aoj_userid, aoj_ids, self.problems_dict, self.points
            )
            self.aoj_users[aoj_userid] = aoj_user


mock_data = MockData()
like_data: dict[int, set[int]] = {}


class MockInternalFunctions(InterfaceInternalFunctions):

    def __init__(self, *args: Any) -> None:
        pass

    def get_points(self, contest_type: int) -> list[int]:
        return mock_data.points[contest_type]

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
                and problem.level == begin
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
