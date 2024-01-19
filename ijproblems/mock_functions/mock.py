import os
import random
from typing import Optional

from fastapi import Request

from ijproblems.internal_functions_interface import (
    AOJUser,
    GitHubLoginInfo,
    InterfaceInternalFunctions,
    Preference,
    ProblemInfo,
    RankingRow,
)


class MockData:
    def __init__(self) -> None:
        self.points = [
            [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330],
            [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900],
        ]

        problems: list[ProblemInfo] = []
        for level, _ in enumerate(self.points[0], 1):
            for n in range(20 - level):
                dummy_id = 1500 + len(problems)
                likes = random.randint(0, level)
                problems.append(
                    ProblemInfo(
                        contest_type=0,
                        name=f"Mock Domestic Problem {dummy_id}",
                        level=level,
                        aoj_id=dummy_id,
                        org="Official",
                        year=2024,
                        used_in="",
                        slot="X",
                        en=True,
                        ja=True,
                        likes=likes,
                        inherited_likes=0,
                        official_editorial="",
                        participated_teams=0,
                        solved_teams=0,
                        user_editorials=[],
                    )
                )

        for level, _ in enumerate(self.points[1], 1):
            for n in range(40 - level):
                dummy_id = 2000 + len(problems)
                ja = False
                en = True
                if random.randint(0, 4) == 0:
                    ja = True
                    en = False
                likes = random.randint(0, level)
                problems.append(
                    ProblemInfo(
                        contest_type=1,
                        name=f"Mock Regional Problem {dummy_id}",
                        level=level,
                        aoj_id=dummy_id,
                        org="Official",
                        year=2024,
                        used_in="",
                        slot="X",
                        en=en,
                        ja=ja,
                        likes=likes,
                        inherited_likes=0,
                        official_editorial="",
                        participated_teams=0,
                        solved_teams=0,
                        user_editorials=[],
                    )
                )
        self.problems = problems

        self.problems_dict = {problem.aoj_id: problem for problem in self.problems}
        n_users = 20
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
                and problem.level >= begin
                and ((preference.ja and problem.ja) or (preference.en and problem.en))
                and not (
                    preference.hide_solved and problem.aoj_id in user_solved_problems
                )
            ],
            key=lambda problem: (-problem.year, problem.aoj_id),
        )

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
        raise NotImplementedError

    def get_user_count(self, contest_type: int) -> int:
        raise NotImplementedError

    def get_github_login_info(self, request: Request) -> Optional[GitHubLoginInfo]:
        if os.environ.get("DUMMY_LOGIN"):
            return GitHubLoginInfo(github_id=123, login="dummy")
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
