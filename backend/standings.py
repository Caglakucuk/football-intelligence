from sqlalchemy import text
from database import engine


def calculate_standings():
    query = text("""
        SELECT
            t.id,
            t.name,
            COUNT(*) AS played,

            SUM(
                CASE
                    WHEN (f.home_team_id = t.id AND f.home_goals > f.away_goals)
                      OR (f.away_team_id = t.id AND f.away_goals > f.home_goals)
                    THEN 1 ELSE 0
                END
            ) AS wins,

            SUM(
                CASE WHEN f.home_goals = f.away_goals
                    THEN 1 ELSE 0
                END
            ) AS draws,

            SUM(
                CASE
                    WHEN (f.home_team_id = t.id AND f.home_goals < f.away_goals)
                      OR (f.away_team_id = t.id AND f.away_goals < f.home_goals)
                    THEN 1 ELSE 0
                END
            ) AS losses,

            SUM(
                CASE WHEN f.home_team_id = t.id
                    THEN f.home_goals ELSE f.away_goals
                END
            ) AS goals_for,

            SUM(
                CASE WHEN f.home_team_id = t.id
                    THEN f.away_goals ELSE f.home_goals
                END
            ) AS goals_against

        FROM teams t
        JOIN fixtures f
            ON t.id = f.home_team_id
            OR t.id = f.away_team_id

        WHERE f.status IN ('FT', 'AET', 'PEN')
          AND f.home_goals IS NOT NULL
          AND f.away_goals IS NOT NULL

        GROUP BY t.id, t.name
    """)

    with engine.connect() as db:
        rows = db.execute(query).mappings().all()

    standings = []

    for row in rows:
        wins = int(row["wins"])
        draws = int(row["draws"])
        goals_for = int(row["goals_for"])
        goals_against = int(row["goals_against"])

        standings.append({
            "team_id": row["id"],
            "team": row["name"],
            "played": row["played"],
            "wins": wins,
            "draws": draws,
            "losses": int(row["losses"]),
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "points": wins * 3 + draws,
        })

    standings.sort(
        key=lambda team: (
            team["points"],
            team["goal_difference"],
            team["goals_for"],
        ),
        reverse=True,
    )

    for position, team in enumerate(standings, start=1):
        team["position"] = position

    return standings