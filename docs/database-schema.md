# Database Schema

FootballIQ uses PostgreSQL to store football competition, team, and fixture data.

## Tables

### leagues
| Column | Type | Nullable | Key |
|---|---|---|---|
| id | INTEGER | No | Primary Key |
| name | VARCHAR(150) | No | |
| country | VARCHAR(100) | Yes | |

### seasons
| Column | Type | Nullable | Key |
|---|---|---|---|
| id | INTEGER | No | Primary Key |
| league_id | INTEGER | No | Foreign Key |
| year | INTEGER | No | |

### teams
| Column | Type | Nullable | Key |
|---|---|---|---|
| id | INTEGER | No | Primary Key |
| name | VARCHAR(150) | No | |
| logo | TEXT | Yes | |

### fixtures
| Column | Type | Nullable | Key |
|---|---|---|---|
| id | INTEGER | No | Primary Key |
| season_id | INTEGER | No | Foreign Key |
| home_team_id | INTEGER | No | Foreign Key |
| away_team_id | INTEGER | No | Foreign Key |
| match_date | TIMESTAMP | No | |
| status | VARCHAR(20) | Yes | |
| home_goals | INTEGER | Yes | |
| away_goals | INTEGER | Yes | |
| updated_at | TIMESTAMP | Yes | |

## Relationships

- seasons.league_id references leagues.id
- fixtures.season_id references seasons.id
- fixtures.home_team_id references teams.id
- fixtures.away_team_id references teams.id

## Data Synchronization

The backend/sync.py script retrieves Turkish Super Lig fixture data
from API-Football for the 2024 season.

The synchronization process uses PostgreSQL UPSERT operations
(INSERT ... ON CONFLICT DO UPDATE) to update existing records
without duplicating fixtures.

Database writes are executed within a transaction.

Synchronization is currently initiated manually.
No automated scheduling is configured.

## Database Hosting

Development: PostgreSQL

Production: Neon PostgreSQL
