from dataclasses import dataclass, asdict
import random

from fastapi import APIRouter
from fastapi.responses import JSONResponse

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

    def __init__(self):
        self.points = {
            0: [20, 30, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870],
            1: [200, 300, 500, 800, 1300, 2100, 3400, 5500, 8900, 14400]
        }

        problems = []
        for _, level in enumerate(self.points[0], 1):
            for n in range(20 - level):
                dummy_id = 1500 + len(problems)
                likes = random.randint(0, level)
                problems.append(
                    MockProblem(0, f"Mock Domestic Problem {dummy_id}", level, dummy_id,
                                "Official", 2024, "", "X", True, True, likes))

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
                    MockProblem(1, f"Mock Regional Problem {dummy_id}", level, dummy_id,
                                "Official", 2024, "", "Y", ja, en, likes))

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
                total_point += sum([user_count * point for user_count, point in zip(user_counts, self.points[contest_type])])
                ranking.append({
                    "aoj_userid": f"user{i:05d}",
                    "total_point": total_point,
                    "counts": user_counts
                })

            self.ranking[contest_type] = sorted(ranking, key=lambda x: -x["total_point"])


mock_data = MockData()


@router.get("/api/points/{contest_type}")
def get_points(contest_type: int) -> JSONResponse:
    return mock_data.points[contest_type]


@router.get("/api/problems/{contest_type}")
def get_problems(contest_type: int, begin: int = 1, end: int = 99) -> JSONResponse:
    return [{
        asdict(problem)
    } for problem in mock_data.problems
        if problem.contest_type == contest_type and problem.level >= begin and problem.level <= end]


@router.get("/api/problems/{contest_type}/count")
def get_problems_counts(contest_type: int) -> JSONResponse:
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
def get_problem_acceptance_count(aoj_id: int) -> JSONResponse:
    return 100


@router.get("/api/problem/{aoj_id}/metainfo")
def get_problem_metainfo(aoj_id: int) -> JSONResponse:
    return asdict(MockProblemMeta(
        "http://example.com",
        200,
        340,
        [],
    ))


@router.get("/api/ranking/{contest_type}")
def get_ranking(contest_type: int, begin: int, end: int) -> JSONResponse:
    if end - begin > mock_data.allowed_max_ranking_retrieval:
        return []
    return mock_data.ranking[begin - 1 : end - 1]


@router.get("/api/ranking/{contest_type}/user_count")
def get_ranking_user_count(contest_type: int) -> JSONResponse:
    return len(mock_data.ranking[contest_type])
