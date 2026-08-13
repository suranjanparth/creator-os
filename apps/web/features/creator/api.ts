export type CreatorProfile = {
  creator_id: string;
  name: string;
  handle: string | null;
  niche: string | null;
  platform: string | null;
  audience: string | null;
  follower_count: number | null;
  created_at: string;
  updated_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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
