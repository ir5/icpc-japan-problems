import abc
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import unquote

from fastapi import Request


@dataclass
class Preference:
    ja: bool
    en: bool
    hide_solved: bool
    contest_type: int
    aoj_userid: str
    rivals: list[str]
    level_scopes: list[int]


AOJAcceptanceInfo = dict[int, list[str]]


@dataclass
class Editorial:
    official: bool
    en: bool
    ja: bool
    url: str

    def unquote_url(self) -> str:
        return unquote(self.url)


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
    editorials: list[Editorial] = field(default_factory=list)
    participated_teams: int = 0
    solved_teams: int = 0
    authors: str = ""


@dataclass
class ProblemInfo(ProblemInfoBase):
    likes: int = 0
    meta: str = ""


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


@dataclass
class GitHubLoginInfo:
    github_id: int
    login: str


class InterfaceInternalFunctions(metaclass=abc.ABCMeta):
    @abstractmethod
    def get_points(self, contest_type: int) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def get_problems(
        self, preference: Preference, user_solved_problems: set[int]
    ) -> list[ProblemInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_problem(self, aoj_id: int) -> Optional[ProblemInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_solved_user_count(self, aoj_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_problems_total_row(self, contest_type: int) -> RankingRow:
        raise NotImplementedError

    @abstractmethod
    def get_problem_acceptance_count(self, aoj_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_global_ranking(
        self, contest_type: int, begin: int, end: int
    ) -> list[RankingRow]:
        raise NotImplementedError

    @abstractmethod
    def get_user_count(self, contest_type: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_github_login_info(self, request: Request) -> Optional[GitHubLoginInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_likes(self, github_id: int) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    def set_like(self, github_id: int, aoj_id: int, value: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_user_local_ranking(
        self, contest_type: int, aoj_userids: list[str]
    ) -> list[RankingRow]:
        raise NotImplementedError

    @abstractmethod
    def get_user_solved_problems(self, aoj_userid: str) -> set[int]:
        raise NotImplementedError
