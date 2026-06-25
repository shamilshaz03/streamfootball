"""
A self-contained mock data source, useful for local development, demos
and tests without depending on any external paid API.

Replace this with a real provider by implementing `FifaDataProvider` and
registering it in `get_provider()` below.
"""
from datetime import datetime, timedelta, timezone

from app.services.fifa_provider.base import FifaDataProvider, FixtureData, ResultData, StandingData, TeamData


class MockFifaProvider(FifaDataProvider):
    GROUPS = ["Group A", "Group B"]

    TEAMS: list[TeamData] = [
        {"name": "Brazil", "short_name": "BRA", "country_code": "BR", "logo_url": "", "group_name": "Group A"},
        {"name": "Argentina", "short_name": "ARG", "country_code": "AR", "logo_url": "", "group_name": "Group A"},
        {"name": "France", "short_name": "FRA", "country_code": "FR", "logo_url": "", "group_name": "Group A"},
        {"name": "Morocco", "short_name": "MAR", "country_code": "MA", "logo_url": "", "group_name": "Group A"},
        {"name": "Spain", "short_name": "ESP", "country_code": "ES", "logo_url": "", "group_name": "Group B"},
        {"name": "Germany", "short_name": "GER", "country_code": "DE", "logo_url": "", "group_name": "Group B"},
        {"name": "Japan", "short_name": "JPN", "country_code": "JP", "logo_url": "", "group_name": "Group B"},
        {"name": "England", "short_name": "ENG", "country_code": "GB", "logo_url": "", "group_name": "Group B"},
    ]

    def get_groups(self) -> list[str]:
        return self.GROUPS

    def get_teams(self) -> list[TeamData]:
        return self.TEAMS

    def get_fixtures(self) -> list[FixtureData]:
        now = datetime.now(timezone.utc)
        return [
            {
                "home_team": "Brazil",
                "away_team": "Argentina",
                "match_date": (now + timedelta(hours=2)).isoformat(),
                "venue": "Lusail Stadium",
                "stage": "Group A",
            },
            {
                "home_team": "France",
                "away_team": "Morocco",
                "match_date": (now + timedelta(days=1, hours=3)).isoformat(),
                "venue": "Al Bayt Stadium",
                "stage": "Group A",
            },
            {
                "home_team": "Spain",
                "away_team": "Germany",
                "match_date": (now + timedelta(days=2, hours=5)).isoformat(),
                "venue": "Education City Stadium",
                "stage": "Group B",
            },
        ]

    def get_results(self) -> list[ResultData]:
        return [
            {"home_team": "Japan", "away_team": "England", "home_score": 2, "away_score": 1},
        ]

    def get_standings(self) -> list[StandingData]:
        return [
            {
                "team": "Brazil", "group_name": "Group A", "played": 2, "won": 2, "drawn": 0,
                "lost": 0, "goals_for": 5, "goals_against": 1, "points": 6, "position": 1,
            },
            {
                "team": "Argentina", "group_name": "Group A", "played": 2, "won": 1, "drawn": 1,
                "lost": 0, "goals_for": 4, "goals_against": 2, "points": 4, "position": 2,
            },
            {
                "team": "Japan", "group_name": "Group B", "played": 1, "won": 1, "drawn": 0,
                "lost": 0, "goals_for": 2, "goals_against": 1, "points": 3, "position": 1,
            },
            {
                "team": "England", "group_name": "Group B", "played": 1, "won": 0, "drawn": 0,
                "lost": 1, "goals_for": 1, "goals_against": 2, "points": 0, "position": 2,
            },
        ]


def get_provider() -> FifaDataProvider:
    """Single place to swap the active data source for the whole app."""
    return MockFifaProvider()
