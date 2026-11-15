import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from standings import calculate_standings
from datetime import date
from fastapi import Query
from analytics import get_teams, get_fixtures, get_team_performance

load_dotenv()

app = FastAPI(title="Football Data Intelligence API")

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"


@app.get("/teams")
def list_teams():
    teams = get_teams()
    return {
        "total": len(teams),
        "teams": teams,
    }


@app.get("/fixtures")
def list_fixtures(
    team_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=400,
            detail="Baslangic tarihi bitis tarihinden sonra olamaz",
        )

    fixtures = get_fixtures(
        team_id=team_id,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "total": len(fixtures),
        "fixtures": fixtures,
    }


@app.get("/teams/{team_id}/performance")
def team_performance(team_id: int):
    performance = get_team_performance(team_id)

    if performance is None:
        raise HTTPException(
            status_code=404,
            detail="Takim bulunamadi",
        )

    return performance

@app.get("/standings")
def get_standings():
    return {
        "league": "Süper Lig",
        "season": 2024,
        "standings": calculate_standings(),
    }
@app.get("/football/matches")
async def get_matches():
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key bulunamadi"
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{BASE_URL}/fixtures",
                headers={"x-apisports-key": API_KEY},
                params={
                    "league": 203,
                    "season": 2024
                }
            )
            response.raise_for_status()
            data = response.json()

        if data.get("errors"):
            raise HTTPException(
                status_code=502,
                detail=data["errors"]
            )

        matches = data.get("response", [])

        return {
            "total_matches": len(matches),
            "matches": [
                {
                    "id": match["fixture"]["id"],
                    "date": match["fixture"]["date"],
                    "status": match["fixture"]["status"]["short"],
                    "home": match["teams"]["home"]["name"],
                    "away": match["teams"]["away"]["name"],
                    "home_goals": match["goals"]["home"],
                    "away_goals": match["goals"]["away"]
                }
                for match in matches
            ]
        }

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Mac verileri alinamadi"
        )
@app.get("/")
def home():
    return {"message": "Football Data Intelligence API calisiyor!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/football/leagues")
async def get_leagues():
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key bulunamadi"
        )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{BASE_URL}/leagues",
                headers={"x-apisports-key": API_KEY},
                params={"current": "true"},
            )
            response.raise_for_status()
            data = response.json()

        if data.get("errors"):
            raise HTTPException(
                status_code=502,
                detail=data["errors"]
            )

        return {
            "results": data.get("results", 0),
            "leagues": data.get("response", [])
        }

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Lig verileri alinamadi"
        )
@app.get("/football/status")   
async def football_status():
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="API key bulunamadi"
        )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{BASE_URL}/status",
                headers={"x-apisports-key": API_KEY},
            )
            response.raise_for_status()
            data = response.json()

        if data.get("errors"):
            raise HTTPException(
                status_code=502,
                detail=data["errors"]
            )

        return data

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="API-Football baglantisi basarisiz"
        )
    