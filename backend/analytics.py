
from datetime import date
from sqlalchemy import text
from database import engine


def get_teams():
    with engine.connect() as db:
        rows = db.execute(text("""
            SELECT id, name, logo
            FROM teams
            ORDER BY name
        """)).mappings().all()
    return [dict(row) for row in rows]


def get_fixtures(team_id=None, date_from=None, date_to=None):
    query = text("""
        SELECT
            f.id,
            f.match_date,
            f.status,
            h.id AS home_team_id,
            h.name AS home,
            a.id AS away_team_id,
            a.name AS away,
            f.home_goals,
            f.away_goals
        FROM fixtures f
        JOIN teams h ON h.id = f.home_team_id
        JOIN teams a ON a.id = f.away_team_id
        JOIN seasons s ON s.id = f.season_id
        WHERE s.league_id = 203 AND s.year = 2024
     AND (
    CAST(:team_id AS INTEGER) IS NULL
    OR f.home_team_id = :team_id
    OR f.away_team_id = :team_id
)
AND (
    CAST(:date_from AS DATE) IS NULL
    OR f.match_date >= CAST(:date_from AS DATE)
)
AND (
    CAST(:date_to AS DATE) IS NULL
    OR f.match_date < CAST(:date_to AS DATE) + INTERVAL '1 day'
)
        ORDER BY f.match_date DESC
    """)

    with engine.connect() as db:
        rows = db.execute(query, {
            "team_id": team_id,
            "date_from": date_from,
            "date_to": date_to,
        }).mappings().all()

    return [dict(row) for row in rows]


def get_team_performance(team_id):
    with engine.connect() as db:
        team = db.execute(
            text("SELECT id, name FROM teams WHERE id = :id"),
            {"id": team_id},
        ).mappings().first()

        if not team:
            return None

        matches = db.execute(text("""
            SELECT
                f.id,
                f.match_date,
                f.home_team_id,
                f.away_team_id,
                f.home_goals,
                f.away_goals
            FROM fixtures f
            JOIN seasons s ON s.id = f.season_id
            WHERE s.league_id = 203
              AND s.year = 2024
              AND (f.home_team_id = :id OR f.away_team_id = :id)
              AND f.status IN ('FT', 'AET', 'PEN')
              AND f.home_goals IS NOT NULL
              AND f.away_goals IS NOT NULL
            ORDER BY f.match_date DESC, f.id DESC
        """), {"id": team_id}).mappings().all()

    results = []
    home_stats = {"played": 0, "wins": 0, "draws": 0, "losses": 0}
    away_stats = {"played": 0, "wins": 0, "draws": 0, "losses": 0}

    for match in matches:
        is_home = match["home_team_id"] == team_id
        scored = match["home_goals"] if is_home else match["away_goals"]
        conceded = match["away_goals"] if is_home else match["home_goals"]

        result = (
            "W" if scored > conceded
            else "D" if scored == conceded
            else "L"
        )

        stats = home_stats if is_home else away_stats
        stats["played"] += 1

        if result == "W":
            stats["wins"] += 1
        elif result == "D":
            stats["draws"] += 1
        else:
            stats["losses"] += 1

        results.append({
            "fixture_id": match["id"],
            "date": match["match_date"].isoformat(),
            "venue": "home" if is_home else "away",
            "scored": scored,
            "conceded": conceded,
            "result": result,
        })

    played = len(results)
    wins = sum(r["result"] == "W" for r in results)
    draws = sum(r["result"] == "D" for r in results)
    losses = sum(r["result"] == "L" for r in results)

    return {
        "team_id": team_id,
        "team": team["name"],
        "season": 2024,
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": round(wins / played * 100, 2) if played else 0,
        "avg_goals_scored": round(
            sum(r["scored"] for r in results) / played, 2
        ) if played else 0,
        "avg_goals_conceded": round(
            sum(r["conceded"] for r in results) / played, 2
        ) if played else 0,
        "home": home_stats,
        "away": away_stats,
        "last_5": results[:5],
    }
