# FootballIQ — Football Data Intelligence

A full-stack football analytics application built with Next.js, TypeScript, FastAPI, and PostgreSQL.

FootballIQ provides an interactive dashboard for exploring Turkish Super Lig match results, league standings, and team performance.

## Live Demo

- Frontend: https://football-intelligence-ivory.vercel.app
- Backend API: https://football-intelligence-aigo.onrender.com
- Interactive API documentation: https://football-intelligence-aigo.onrender.com/docs

## Features

- Interactive football analytics dashboard
- Turkish Super Lig 2024 season data
- Team directory and performance analysis
- Match listings with filtering capabilities
- League standings
- Data visualization using Recharts
- Responsive interface built with Tailwind CSS
- REST API built with FastAPI

## Technology Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- Recharts
- SWR
- Lucide React

### Backend
- Python
- FastAPI
- SQLAlchemy
- HTTPX
- PostgreSQL

### Infrastructure
- Vercel — frontend hosting
- Render — backend hosting
- Neon — managed PostgreSQL database
- GitHub — version control

## Architecture

The frontend communicates with FastAPI through a Next.js API proxy.

FastAPI provides database-backed endpoints for teams, fixtures, standings, and team performance.

Football data is retrieved from API-Football and stored in PostgreSQL using a separate synchronization script.

Architecture overview:

    Browser
       |
       v
    Next.js Frontend (Vercel)
       |
       v
    Next.js API Proxy
       |
       v
    FastAPI Backend (Render)
       |
       v
    PostgreSQL Database (Neon)

Data ingestion:

    API-Football
       |
       v
    Python Synchronization Script
       |
       v
    PostgreSQL Database

## Project Structure

    backend/
      main.py
      database.py
      analytics.py
      standings.py
      sync.py
      requirements.txt
      requirements-dev.txt
      .env.example
      tests/
        test_api.py

    frontend/
      app/
      components/
      package.json

    docs/
      database-schema.md

    README.md

## Local Installation

### Prerequisites

- Python 3.13
- Node.js compatible with Next.js 16
- PostgreSQL
- npm
- API-Football API key

### 1. Clone the Repository

    git clone https://github.com/Caglakucuk/football-intelligence.git
    cd football-intelligence

### 2. Configure the Backend

    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Create a .env file based on backend/.env.example.

Configure the following variables:

    DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/DATABASE_NAME
    API_FOOTBALL_KEY=YOUR_API_FOOTBALL_KEY

Use your own database credentials and API key.

The PostgreSQL schema must be initialized before running database-backed endpoints. See docs/database-schema.md for the table structure and relationships.

Start the backend:

    uvicorn main:app --reload

The API will be available at:

    http://localhost:8000

Interactive documentation:

    http://localhost:8000/docs

### 3. Configure the Frontend

Open a separate terminal:

    cd frontend
    npm install

Create frontend/.env.local with:

    API_BASE_URL=http://localhost:8000

Start the frontend:

    npm run dev

Open:

    http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API welcome message |
| GET | /health | Health check |
| GET | /teams | List teams |
| GET | /fixtures | List and filter fixtures |
| GET | /teams/{team_id}/performance | Team performance statistics |
| GET | /standings | League standings |
| GET | /football/matches | Retrieve fixtures from API-Football |
| GET | /football/leagues | Retrieve league information from API-Football |
| GET | /football/status | Retrieve API-Football account status |

The /fixtures endpoint supports optional query parameters:

- team_id
- date_from
- date_to

Invalid date ranges return HTTP 400.

## Database Schema

The PostgreSQL database contains four main tables:

- leagues
- seasons
- teams
- fixtures

Foreign keys connect seasons to leagues and fixtures to seasons and teams.

Full database documentation:

[Database Schema](docs/database-schema.md)

## Data Synchronization Strategy

The backend/sync.py script retrieves Turkish Super Lig fixture data from API-Football.

Current configuration:

- League ID: 203
- Season: 2024
- Data source: API-Football

Run synchronization manually:

    cd backend
    python sync.py

The synchronization script:

1. Requests fixture data from API-Football.
2. Checks for API errors and empty responses.
3. Inserts or updates league and season records.
4. Inserts or updates team records.
5. Inserts or updates fixtures.
6. Uses PostgreSQL transactions to keep database writes consistent.

PostgreSQL UPSERT operations prevent duplicate fixture records when synchronization is repeated.

### API Usage and Rate Limit Considerations

The application separates stored analytics data from direct API-Football requests.

Database-backed analytics endpoints can serve existing data without requesting the external football API on every dashboard query.

The synchronization script is run manually. This allows API usage to be controlled by deciding when a refresh is necessary.

The direct API-Football endpoints currently make external requests when called.

Automated scheduling, response caching, automatic retries, and explicit rate-limit enforcement are not currently implemented.

Potential future improvements include scheduled synchronization, caching, request quotas, and retry strategies for temporary API failures.

## Automated Tests

The backend includes two automated tests using pytest:

1. Verify that the health endpoint returns HTTP 200 and the expected response.
2. Verify that invalid fixture date ranges return HTTP 400.

Install development dependencies:

    cd backend
    pip install -r requirements.txt
    pip install -r requirements-dev.txt

Run the tests:

    python -m pytest tests/test_api.py -v

Both tests passed during local development.

## Security

- API keys and database credentials are provided through environment variables.
- Real credentials must never be committed to GitHub.
- The repository includes an example environment configuration.
- Production credentials are configured through hosting provider environment settings.

## Deployment

- Frontend: Vercel, with frontend as the root directory.
- Backend: Render, with backend as the root directory.
- Database: Neon PostgreSQL.

The frontend uses API_BASE_URL to communicate with the deployed FastAPI backend.

## Technical Decisions and Limitations

FastAPI was selected for its lightweight Python-based REST API development and automatic OpenAPI documentation.

PostgreSQL provides relational integrity for leagues, seasons, teams, and fixtures.

SQLAlchemy is used for database access, while SQL UPSERT operations support repeatable data synchronization.

Next.js and TypeScript provide a structured frontend architecture. Recharts supports interactive data visualization, and SWR supports frontend data fetching.

The interface uses Tailwind CSS and custom React components rather than relying on the shadcn/ui component library.

The application currently focuses on the Turkish Super Lig 2024 season. Data synchronization is manual, and external API rate-limit controls are an area for future improvement.
