export type DnaShare = {
  name: string;
  count: number;
  share: number;
};

export type DnaFormatPerformance = {
  name: string;
  average_engagement_rate: number;
  sample_size: number;
};

export type DnaInsight = {
  title: string;
  summary: string;
  evidence: string | null;
  sample_size: number | null;
};

export type DnaIdentity = {
  name: string;
  handle: string | null;
  niche: string | null;
  audience: string | null;
  platform: string | null;
  follower_count: number | null;
};

export type DnaEngagementBenchmark = {
  average_views: number;
  average_engagement_rate: number;
  sample_size: number;
};

export type DnaData = {
  data_source: "development" | "empty";
  identity: DnaIdentity | null;
  total_posts: number;
  platforms: DnaShare[];
  formats: DnaShare[];
  categories: DnaShare[];
  best_format: DnaFormatPerformance | null;
  engagement_benchmark: DnaEngagementBenchmark | null;
  insights: DnaInsight[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchCreatorDna(creatorId: string): Promise<DnaData> {
  if (!creatorId) {
    throw new Error("No creator selected");
  }

  const response = await fetch(`${apiBaseUrl}/api/v1/creator-dna?creator_id=${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Creator DNA request failed with status ${response.status}`);
  }

  return (await response.json()) as DnaData;
}
