
import type {
  FixturesResponse,
  StandingsResponse,
  TeamsResponse,
  TeamPerformance,
} from "./types";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`/api/${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);

    const message =
      typeof payload?.error === "string"
        ? payload.error
        : typeof payload?.detail === "string"
          ? payload.detail
          : `Backend request failed (${response.status})`;

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const getStandings = () =>
  request<StandingsResponse>("standings");

export const getTeams = () =>
  request<TeamsResponse>("teams");

export const getFixtures = (query = "") =>
  request<FixturesResponse>(
    `fixtures${query ? `?${query}` : ""}`
  );

export const getPerformance = (teamId: number) =>
  request<TeamPerformance>(
    `teams/${teamId}/performance`
  );
