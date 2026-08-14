export type Recommendation = {
  tag: string;
  title: string;
  description: string;
  evidence: string | null;
  sample_size: number | null;
  action: string;
  href: string | null;
};

export type RecommendationOpportunity = {
  title: string;
  description: string;
  href: string;
};

export type RecommendationsData = {
  data_source: "development" | "empty";
  priority_signal: string;
  priority_copy: string;
  recommendations: Recommendation[];
  opportunities: RecommendationOpportunity[];
  total_posts: number;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchRecommendations(creatorId: string): Promise<RecommendationsData> {
  if (!creatorId) {
    throw new Error("No creator selected");
  }

  const response = await fetch(`${apiBaseUrl}/api/v1/recommendations?creator_id=${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Recommendations request failed with status ${response.status}`);
  }

  return (await response.json()) as RecommendationsData;
}
