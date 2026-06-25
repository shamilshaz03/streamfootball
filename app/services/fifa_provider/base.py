"""
Provider abstraction for external tournament data (teams, fixtures,
results, standings, groups).

Today only `MockFifaProvider` exists, seeded with sample data. To plug in
a real data vendor later (e.g. a paid football-data API), implement a new
subclass of `FifaDataProvider` and swap it in `get_provider()` below -
nothing else in the codebase needs to change.
"""
from abc import ABC, abstractmethod
from typing import TypedDict


class TeamData(TypedDict):
    name: str
    short_name: str
    country_code: str
    logo_url: str
    group_name: str


class FixtureData(TypedDict):
    home_team: str
    away_team: str
    match_date: str  # ISO 8601
    venue: str
    stage: str


class ResultData(TypedDict):
    home_team: str
    away_team: str
    home_score: int
    away_score: int


class StandingData(TypedDict):
    team: str
    group_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    points: int
    position: int


class FifaDataProvider(ABC):
    """Common interface every tournament data source must implement."""

    @abstractmethod
    def get_groups(self) -> list[str]:
        """Return the list of group names, e.g. ['Group A', 'Group B']."""

    @abstractmethod
    def get_teams(self) -> list[TeamData]:
        """Return all teams competing in the tournament."""

    @abstractmethod
    def get_fixtures(self) -> list[FixtureData]:
        """Return all scheduled (not yet played) fixtures."""

    @abstractmethod
    def get_results(self) -> list[ResultData]:
        """Return completed match results."""

    @abstractmethod
    def get_standings(self) -> list[StandingData]:
        """Return the current points table."""
