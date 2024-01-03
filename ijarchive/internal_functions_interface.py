import abc
from dataclasses import dataclass
from typing import Optional


@dataclass
class DifficultyScope:
    level_begin: int
    level_end: int


@dataclass
class Preference:
    contest_type: int
    aoj_userid: str
    rivals: list[str]
    exclude_solved: bool
    difficulty_scope: list[DifficultyScope]


AOJAcceptanceInfo = dict[int, list[str]]


@dataclass
class ProblemInfoBase:
    contest_type: int
    name: str
    level: int
    aoj_id: int
    org: str
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
