import random
from dataclasses import asdict, dataclass
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@dataclass
class MockProblem:
    contest_type: int
    name: str
    level: int
    aoj_id: int
    org: str
    year: int
    used_in: str
    slot: str
    en_statement: bool
    ja_statement: bool
    likes: int


@dataclass
class MockProblemMeta:
    official_editorial: str
    contest_teams: int
    solved_teams: int
    user_editorials: list[str]


class MockData:
    def __init__(self) -> None:
        self.points = {
            0: [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870],
            1: [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900, 14400],
        }

        problems: list[MockProblem] = []
        for _, level in enumerate(self.points[0], 1):
            for n in range(20 - level):
                dummy_id = 1500 + len(problems)
                likes = random.randint(0, level)
                problems.append(
                    MockProblem(
                        0,
                        f"Mock Domestic Problem {dummy_id}",
                        level,
                        dummy_id,
                        "Official",
                        2024,
                        "",
                        "X",
                        True,
                        True,
                        likes,
                    )
                )

        for _, level in enumerate(self.points[1], 1):
            for n in range(40 - level):
                dummy_id = 2000 + len(problems)
                ja = False
                en = True
                if random.randint(0, 4) == 0:
                    ja = True
                    en = False
                likes = random.randint(0, level)
                problems.append(
                    MockProblem(
                        1,
                        f"Mock Regional Problem {dummy_id}",
                        level,
                        dummy_id,
                        "Official",
                        2024,
                        "",
                        "Y",
                        ja,
                        en,
                        likes,
                    )
                )

        self.problems = problems


mock_data = MockData()


@router.get("/api/points/{contest_type}")
def get_points(contest_type: int) -> Any:
    return mock_data.points[contest_type]


@router.get("/api/problems/{contest_type}")
def get_problems(contest_type: int, begin: int = 1, end: int = 99) -> Any:
    return [
        {asdict(problem)}
        for problem in mock_data.problems
        if problem.contest_type == contest_type
        and problem.level >= begin
        and problem.level <= end
    ]


@router.get("/api/problems/{contest_type}/count")
def get_problems_counts(contest_type: int) -> Any:
    counts = [0] * len(mock_data.points[contest_type])
    total_points = 0
    for problem in mock_data.problems:
        if problem.contest_type != contest_type:
            continue
        level = problem.level - 1
        counts[level - 1] += 1
        total_points += mock_data.points[contest_type][level - 1]

    return {
        "total_points": total_points,
        "counts": counts,
    }


@router.get("/api/problem/{aoj_id}/acceptance_count")
def get_problem_acceptance_count(aoj_id: int) -> Any:
    return 100


@router.get("/api/problem/{aoj_id}/metainfo")
def get_problem_metainfo(aoj_id: int) -> Any:
    return asdict(
        MockProblemMeta(
            "http://example.com",
            200,
            340,
            [],
        )
    )
