"""
Pulls data from the active `FifaDataProvider` and upserts it into the
database. This is what the admin "Sync Tournament Data" action (and,
in the future, a scheduled job) would call.
"""
from sqlalchemy.orm import Session

from app.models.standing import Standing
from app.models.team import Team
from app.models.tournament import Group, Tournament
from app.services.fifa_provider.base import FifaDataProvider


def sync_tournament_data(db: Session, tournament: Tournament, provider: FifaDataProvider) -> dict:
    """Idempotent sync: safe to run repeatedly, e.g. on a schedule."""
    groups_by_name: dict[str, Group] = {g.name: g for g in tournament.groups}
    for group_name in provider.get_groups():
        if group_name not in groups_by_name:
            group = Group(tournament_id=tournament.id, name=group_name)
            db.add(group)
            db.flush()
            groups_by_name[group_name] = group

    teams_by_name: dict[str, Team] = {t.name: t for t in tournament.teams}
    for team_data in provider.get_teams():
        group = groups_by_name.get(team_data["group_name"])
        if team_data["name"] in teams_by_name:
            team = teams_by_name[team_data["name"]]
            team.short_name = team_data["short_name"]
            team.country_code = team_data["country_code"]
            team.logo_url = team_data["logo_url"] or team.logo_url
            team.group_id = group.id if group else team.group_id
        else:
            team = Team(
                tournament_id=tournament.id,
                name=team_data["name"],
                short_name=team_data["short_name"],
                country_code=team_data["country_code"],
                logo_url=team_data["logo_url"],
                group_id=group.id if group else None,
            )
            db.add(team)
            db.flush()
            teams_by_name[team.name] = team

    for standing_data in provider.get_standings():
        team = teams_by_name.get(standing_data["team"])
        if not team:
            continue
        group = groups_by_name.get(standing_data["group_name"])
        existing = db.query(Standing).filter(Standing.team_id == team.id).one_or_none()
        if existing is None:
            existing = Standing(tournament_id=tournament.id, team_id=team.id)
            db.add(existing)
        existing.group_id = group.id if group else None
        existing.played = standing_data["played"]
        existing.won = standing_data["won"]
        existing.drawn = standing_data["drawn"]
        existing.lost = standing_data["lost"]
        existing.goals_for = standing_data["goals_for"]
        existing.goals_against = standing_data["goals_against"]
        existing.points = standing_data["points"]
        existing.position = standing_data["position"]

    db.commit()
    return {
        "groups": len(groups_by_name),
        "teams": len(teams_by_name),
        "standings": len(provider.get_standings()),
    }
