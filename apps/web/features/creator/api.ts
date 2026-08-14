export type CreatorProfile = {
  creator_id: string;
  name: string;
  handle: string | null;
  profile_url: string | null;
  niche: string | null;
  platform: string | null;
  audience: string | null;
  follower_count: number | null;
  created_at: string;
  updated_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function createCreatorProfile(profile: {
  creator_id: string;
  name: string;
  handle?: string | null;
  profile_url?: string | null;
  niche?: string | null;
  platform?: string | null;
  audience?: string | null;
  follower_count?: number | null;
}): Promise<CreatorProfile> {
  const response = await fetch(`${apiBaseUrl}/api/v1/creators`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    const error = await extractErrorMessage(response);
    throw new Error(error);
  }

  return (await response.json()) as CreatorProfile;
}

export async function fetchCreatorProfile(creatorId: string): Promise<CreatorProfile> {
  const response = await fetch(`${apiBaseUrl}/api/v1/creators/${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Creator profile request failed with status ${response.status}`);
  }

  return (await response.json()) as CreatorProfile;
}

export async function fetchCreatorProfiles(): Promise<CreatorProfile[]> {
  const response = await fetch(`${apiBaseUrl}/api/v1/creators`);

  if (!response.ok) {
    throw new Error(`Creator profiles request failed with status ${response.status}`);
  }

  return (await response.json()) as CreatorProfile[];
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item: { msg?: string }) => item.msg ?? "Invalid value")
        .join("; ");
    }
  } catch {
    // Non-JSON error body; fall through to the status-based message.
  }
  return `Creator request failed with status ${response.status}`;
}
