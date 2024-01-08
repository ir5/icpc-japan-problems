import random
from typing import Optional

from ijarchive.internal_functions_interface import (
    InterfaceInternalFunctions,
    Preference,
    ProblemInfo,
    RankingRow,
)


class MockData:
    def __init__(self):
        self.points = {
            0: [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330],
            1: [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900],
        }

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
        print(self.problems)

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


mock_data = MockData()


class MockInternalFunctions(InterfaceInternalFunctions):
    def get_points(self, contest_type: int) -> list[int]:
        return mock_data.points[contest_type]

    def get_problems(self, preference: Preference) -> list[ProblemInfo]:
        contest_type = preference.contest_type
        begin = preference.level_scopes[contest_type].begin
        end = preference.level_scopes[contest_type].end
        return [
            problem
            for problem in mock_data.problems
            if problem.contest_type == contest_type
            and problem.level >= begin
            and problem.level <= end
        ]

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

    def get_user_preference(self, github_id: Optional[int] = None) -> Preference:
        raise NotImplementedError

    def set_user_preference(
        self, preference: Preference, github_id: Optional[int] = None
    ) -> bool:
        raise NotImplementedError

    def get_user_local_ranking(self, aoj_userids: list[str]) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_solved_problems(self, aoj_userid: str) -> list[int]:
        raise NotImplementedError
