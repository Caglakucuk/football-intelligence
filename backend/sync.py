import os

import httpx
from dotenv import load_dotenv
from sqlalchemy import text

from database import engine

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

LEAGUE_ID = 203
SEASON = 2024


def sync_matches():
    if not API_KEY:
        raise RuntimeError("API_FOOTBALL_KEY bulunamadi")

    print("API-Football'dan maclar getiriliyor...")

    with httpx.Client(timeout=40.0) as client:
        response = client.get(
            f"{BASE_URL}/fixtures",
            headers={"x-apisports-key": API_KEY},
            params={"league": LEAGUE_ID, "season": SEASON},
        )
        response.raise_for_status()
        data = response.json()

    if data.get("errors"):
        raise RuntimeError(f"API hatasi: {data['errors']}")

    matches = data.get("response", [])

    if not matches:
        raise RuntimeError("API hic mac dondurmedi. Kayit yapilmadi.")

    with engine.begin() as db:
        db.execute(
            text("""
                INSERT INTO leagues (id, name, country)
                VALUES (:id, :name, :country)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name,
                    country = EXCLUDED.country
            """),
            {
                "id": LEAGUE_ID,
                "name": "Süper Lig",
                "country": "Turkey",
            },
        )

        season_id = db.execute(
            text("""
                INSERT INTO seasons (league_id, year)
                VALUES (:league_id, :year)
                ON CONFLICT (league_id, year)
                DO UPDATE SET year = EXCLUDED.year
                RETURNING id
            """),
            {"league_id": LEAGUE_ID, "year": SEASON},
        ).scalar_one()

        for match in matches:
            fixture = match["fixture"]
            home = match["teams"]["home"]
            away = match["teams"]["away"]

            for team in (home, away):
                db.execute(
                    text("""
                        INSERT INTO teams (id, name, logo)
                        VALUES (:id, :name, :logo)
                        ON CONFLICT (id) DO UPDATE
                        SET name = EXCLUDED.name,
                            logo = EXCLUDED.logo
                    """),
                    {
                        "id": team["id"],
                        "name": team["name"],
                        "logo": team.get("logo"),
                    },
                )

            db.execute(
                text("""
                    INSERT INTO fixtures (
                        id, season_id, home_team_id, away_team_id,
                        match_date, status, home_goals, away_goals
                    )
                    VALUES (
                        :id, :season_id, :home_team_id, :away_team_id,
                        :match_date, :status, :home_goals, :away_goals
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        season_id = EXCLUDED.season_id,
                        home_team_id = EXCLUDED.home_team_id,
                        away_team_id = EXCLUDED.away_team_id,
                        match_date = EXCLUDED.match_date,
                        status = EXCLUDED.status,
                        home_goals = EXCLUDED.home_goals,
                        away_goals = EXCLUDED.away_goals,
                        updated_at = NOW()
                """),
                {
                    "id": fixture["id"],
                    "season_id": season_id,
                    "home_team_id": home["id"],
                    "away_team_id": away["id"],
                    "match_date": fixture["date"],
                    "status": fixture["status"]["short"],
                    "home_goals": match["goals"]["home"],
                    "away_goals": match["goals"]["away"],
                },
            )

    print(f"Basarili! {len(matches)} mac veritabanina kaydedildi.")


if __name__ == "__main__":
    sync_matches()