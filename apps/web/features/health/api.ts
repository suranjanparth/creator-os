export type HealthResponse = {
  status: string;
  service: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);

  if (!response.ok) {
    throw new Error(`Backend health check failed with status ${response.status}`);
  }

  return (await response.json()) as HealthResponse;
}
