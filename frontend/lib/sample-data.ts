import type { Fixture, FixturesResponse, StandingsResponse, Team, TeamPerformance, TeamsResponse } from './types'

export const sampleTeams: Team[] = [
  { id: 1, name: 'Galatasaray', logo: null },
  { id: 2, name: 'Fenerbahçe', logo: null },
  { id: 3, name: 'Beşiktaş', logo: null },
  { id: 4, name: 'Trabzonspor', logo: null },
  { id: 5, name: 'Başakşehir', logo: null },
  { id: 6, name: 'Samsunspor', logo: null },
]

const records = [
  [36, 29, 5, 2, 91, 31],
  [36, 26, 6, 4, 90, 39],
  [36, 16, 8, 12, 63, 47],
  [36, 13, 9, 14, 55, 49],
  [36, 16, 6, 14, 58, 42],
  [36, 16, 7, 13, 51, 41],
]

export const sampleStandings: StandingsResponse & { preview_only: true } = {
  league: 'Turkish Süper Lig',
  season: 2024,
  preview_only: true,
  standings: sampleTeams.map((team, index) => {
    const [played, wins, draws, losses, goals_for, goals_against] = records[index]
    return { team_id: team.id, team: team.name, played, wins, draws, losses, goals_for, goals_against, goal_difference: goals_for - goals_against, points: wins * 3 + draws, position: index + 1 }
  }).sort((a, b) => b.points - a.points).map((row, index) => ({ ...row, position: index + 1 })),
}

const sampleFixtures: Fixture[] = [
  { id: 1, match_date: '2025-05-18', status: 'FT', home_team_id: 1, home: 'Galatasaray', away_team_id: 2, away: 'Fenerbahçe', home_goals: 3, away_goals: 0 },
  { id: 2, match_date: '2025-05-18', status: 'FT', home_team_id: 3, home: 'Beşiktaş', away_team_id: 4, away: 'Trabzonspor', home_goals: 2, away_goals: 1 },
  { id: 3, match_date: '2025-05-11', status: 'FT', home_team_id: 2, home: 'Fenerbahçe', away_team_id: 5, away: 'Başakşehir', home_goals: 1, away_goals: 0 },
  { id: 4, match_date: '2025-05-11', status: 'FT', home_team_id: 6, home: 'Samsunspor', away_team_id: 1, away: 'Galatasaray', home_goals: 0, away_goals: 2 },
  { id: 5, match_date: '2025-05-04', status: 'FT', home_team_id: 4, home: 'Trabzonspor', away_team_id: 2, away: 'Fenerbahçe', home_goals: 1, away_goals: 1 },
  { id: 6, match_date: '2025-05-04', status: 'FT', home_team_id: 5, home: 'Başakşehir', away_team_id: 3, away: 'Beşiktaş', home_goals: 2, away_goals: 3 },
]

function filterFixtures(query: string): Fixture[] {
  const params = new URLSearchParams(query)
  return sampleFixtures.filter((fixture) => {
    const teamId = Number(params.get('team_id'))
    const from = params.get('date_from')
    const to = params.get('date_to')
    return (!teamId || fixture.home_team_id === teamId || fixture.away_team_id === teamId)
      && (!from || fixture.match_date >= from)
      && (!to || fixture.match_date <= to)
  })
}

export const getSampleResponse = (path: string): unknown => {
  if (path === 'standings') return sampleStandings
  if (path === 'teams') return { total: sampleTeams.length, teams: sampleTeams, preview_only: true } satisfies TeamsResponse & { preview_only: true }
  if (path.startsWith('fixtures')) {
    const fixtures = filterFixtures(path.split('?')[1] ?? '')
    return { total: fixtures.length, fixtures, preview_only: true } satisfies FixturesResponse & { preview_only: true }
  }
  const performanceMatch = path.match(/^teams\/(\d+)\/performance$/)
  if (performanceMatch) {
    const team = sampleTeams.find((item) => item.id === Number(performanceMatch[1]))
    if (team) return {
      team_id: team.id, team: team.name, season: 2024, played: 36, wins: 20, draws: 8, losses: 8,
      win_rate: 55.6, avg_goals_scored: 1.75, avg_goals_conceded: 1.08,
      home: { played: 18, wins: 12, draws: 4, losses: 2 }, away: { played: 18, wins: 8, draws: 4, losses: 6 },
      last_5: [
        { fixture_id: 1, date: '2025-05-18', venue: 'home', scored: 3, conceded: 0, result: 'W' },
        { fixture_id: 2, date: '2025-05-11', venue: 'away', scored: 2, conceded: 0, result: 'W' },
        { fixture_id: 3, date: '2025-05-04', venue: 'home', scored: 1, conceded: 0, result: 'W' },
        { fixture_id: 4, date: '2025-04-27', venue: 'away', scored: 1, conceded: 2, result: 'L' },
        { fixture_id: 5, date: '2025-04-20', venue: 'home', scored: 2, conceded: 2, result: 'D' },
      ], preview_only: true,
    } satisfies TeamPerformance & { preview_only: true }
  }
  throw new Error('No preview sample is available for this endpoint.')
}
