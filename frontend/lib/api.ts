
import type {
  FixturesResponse,
  StandingsResponse,
  TeamsResponse,
  TeamPerformance,
} from "./types";

const sleep = (ms: number) =>
  new Promise<void>((resolve) => setTimeout(resolve, ms));

async function request<T>(path: string): Promise<T> {
  const maxAttempts = 3;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
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

        const error = new Error(message);

        if (
          attempt === maxAttempts ||
          ![502, 503, 504].includes(response.status)
        ) {
          throw error;
        }

        await sleep(attempt * 1500);
        continue;
      }

      return (await response.json()) as T;
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error;
      }

      if (
        error instanceof Error &&
        error.message.startsWith("Backend request failed (")
      ) {
        throw error;
      }

      await sleep(attempt * 1500);
    }
  }

  throw new Error("Unable to load football data.");
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
