import abc
from dataclasses import dataclass
from typing import Optional


@dataclass
class Preference:
    ja: bool
    en: bool
    contest_type: int
    aoj_userid: str
    rivals: list[str]
    hide_solved: bool
    level_scopes: list[int]


AOJAcceptanceInfo = dict[int, list[str]]


@dataclass
class ProblemInfoBase:
    contest_type: int
    name: str
    level: int
    aoj_id: int
    org: str
    year: int
    used_in: str
    slot: str
    en: bool
    ja: bool
    inherited_likes: int
    official_editorial: str
    participated_teams: int
    solved_teams: int
    user_editorials: list[str]


@dataclass
class ProblemInfo(ProblemInfoBase):
    likes: int


@dataclass
class RankingRow:
    aoj_userid: str
    total_point: int
    total_solved: int
    solved_counts: list[int]


@dataclass
class AOJUser:
    aoj_userid: str
    total_point: list[int]
    total_solved: list[int]
    solved_counts: list[list[int]]
    aoj_ids: set[int]

    @classmethod
    def from_aoj_ids(cls, aoj_userid: str, aoj_ids: set[int], problems: dict[int, ProblemInfoBase], points: list[list[int]]):
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
            aoj_ids=aoj_ids
        )

    def to_ranking_row(self, contest_type):
        return RankingRow(
            aoj_userid=self.aoj_userid,
            total_point=self.total_point[contest_type],
            total_solved=self.total_solved[contest_type],
            solved_counts=self.solved_counts[contest_type],
        )


class InterfaceInternalFunctions(metaclass=abc.ABCMeta):
    def get_points(self, contest_type: int) -> list[int]:
        raise NotImplementedError

    def get_problems(self, preference: Preference) -> list[ProblemInfo]:
        raise NotImplementedError

    def get_problems_total_row(self, contest_type: int) -> RankingRow:
        raise NotImplementedError

    def get_problem_acceptance_count(self, aoj_id: int) -> int:
        raise NotImplementedError

    def get_global_ranking(
        self, contest_type: int, begin: int, end: int
    ) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_count(self, contest_type) -> int:
        raise NotImplementedError

    def get_likes(self, github_id: int) -> list[int]:
        raise NotImplementedError

    def set_like(self, github_id: int, aoj_id: int, value: int) -> bool:
        raise NotImplementedError

    def get_user_local_ranking(self, aoj_userids: list[str]) -> list[RankingRow]:
        raise NotImplementedError

    def get_user_solved_problems(self, aoj_userid: str) -> list[int]:
        raise NotImplementedError
