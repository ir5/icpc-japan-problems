import random
from typing import Optional

from ijarchive.internal_functions_interface import (
    AOJUser,
    InterfaceInternalFunctions,
    Preference,
    ProblemInfo,
    RankingRow,
)


class MockData:
    def __init__(self):
        self.points = [
            [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330],
            [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900],
        ]

        problems = []
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

        self.n_users = 20000
        self.allowed_max_ranking_retrieval = 200
        self.ranking = {}
        for contest_type in (0, 1):
            ranking = []

            counts = [0] * len(self.points[contest_type])
            for problem in self.problems:
                if problem.contest_type != contest_type:
                    continue
                level = problem.level - 1
                counts[level - 1] += 1

            total_point = 0
            for i in range(self.n_users):
                user_counts = [random.randint(0, count + 1) for count in counts]
                total_point += sum(
                    [
                        user_count * point
                        for user_count, point in zip(
                            user_counts, self.points[contest_type]
                        )
                    ]
                )
                ranking.append(
                    {
                        "aoj_userid": f"user{i:05d}",
                        "total_point": total_point,
                        "counts": user_counts,
                    }
                )

            self.ranking[contest_type] = sorted(
                ranking, key=lambda x: -x["total_point"]
            )

        problems_dict = {problem.aoj_id: problem for problem in self.problems}

        n_users = 20
        self.aoj_users: AOJUser = {}
        for i in range(n_users):
            aoj_userid = f"user{i}"
            aoj_ids = set()
            for problem in self.problems:
                if random.randint(0, 3) == 0:
                    aoj_ids.add(problem.aoj_id)

            aoj_user = AOJUser.from_aoj_ids(aoj_userid, aoj_ids, problems_dict, self.points)
            self.aoj_users[aoj_userid] = aoj_user


mock_data = MockData()


class MockInternalFunctions(InterfaceInternalFunctions):
    def get_points(self, contest_type: int) -> list[int]:
        return mock_data.points[contest_type]

    def get_problems(self, preference: Preference, user_solved_problems: set[int]) -> list[ProblemInfo]:
        contest_type = preference.contest_type
        begin = preference.level_scopes[contest_type]
        return sorted([
            problem
            for problem in mock_data.problems
            if problem.contest_type == contest_type
            and problem.level >= begin
            and problem.ja <= preference.ja
            and problem.en <= preference.en
            and not (preference.hide_solved and problem.aoj_id in user_solved_problems)
        ], key=lambda problem: (-problem.year, problem.aoj_id))

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
        return mock_data.ranking[contest_type][begin - 1 : end - 1]

    def get_user_count(self, contest_type) -> int:
        return len(mock_data.ranking[contest_type])

    def get_likes(self, github_id: int) -> list[int]:
        return []

    def set_like(self, github_id: int, aoj_id: int, value: int) -> bool:
        raise NotImplementedError

    def get_user_local_ranking(self, contest_type: int, aoj_userids: list[str]) -> list[RankingRow]:
        rows: list[RankingRow] = []
        for aoj_userid in aoj_userids:
            if aoj_userid not in mock_data.aoj_users:
                empty_row = RankingRow(
                    aoj_userid=aoj_userid,
                    total_point=0,
                    total_solved=0,
                    solved_counts=[0] * len(mock_data.points[contest_type])
                )
                rows.append(empty_row)
            else:
                user = mock_data.aoj_users[aoj_userid]
                rows.append(user.to_ranking_row(contest_type))
            rows = sorted(rows, key=lambda row: (row.total_point, row.aoj_userid), reverse=True)
        return rows

    def get_user_solved_problems(self, aoj_userid: str) -> set[int]:
        if aoj_userid in mock_data.aoj_users:
            user = mock_data.aoj_users[aoj_userid]
            return user.aoj_ids
        return set()
