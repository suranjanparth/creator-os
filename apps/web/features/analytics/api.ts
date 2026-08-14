export type AnalyticsTotals = {
  views: number;
  likes: number;
  comments: number;
  shares: number;
  engagements: number;
  average_engagement_rate: number;
};

export type AnalyticsPlatform = {
  platform: string;
  posts: number;
  views: number;
  share: number;
};

export type AnalyticsPost = {
  id: string;
  title: string;
  platform: string;
  content_type: string;
  views: number | null;
  engagement_rate: number | null;
  published_at: string | null;
};

export type AnalyticsTrendPoint = {
  date: string;
  views: number;
};

export type AnalyticsEngagementAnatomy = {
  likes_share: number;
  comments_share: number;
  shares_share: number;
  sample_size: number;
};

export type AnalyticsData = {
  data_source: "development" | "empty";
  total_posts: number;
  totals: AnalyticsTotals | null;
  platform_breakdown: AnalyticsPlatform[];
  top_posts: AnalyticsPost[];
  trend: AnalyticsTrendPoint[];
  engagement_anatomy: AnalyticsEngagementAnatomy | null;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchAnalytics(creatorId: string): Promise<AnalyticsData> {
  if (!creatorId) {
    throw new Error("No creator selected");
  }

  const response = await fetch(`${apiBaseUrl}/api/v1/analytics?creator_id=${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Analytics request failed with status ${response.status}`);
  }

  return (await response.json()) as AnalyticsData;
}
