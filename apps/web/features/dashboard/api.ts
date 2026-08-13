import { DEVELOPMENT_CREATOR_ID } from "@/features/creator/scope";

export type DashboardCreator = {
  name: string;
  handle: string | null;
  niche: string | null;
  audience: string | null;
  followers: number | null;
};

export type DashboardMetric = {
  label: string;
  value: number | null;
  change: number | null;
  detail: string | null;
};

export type DashboardContent = {
  id: string;
  title: string;
  platform: string;
  content_type: string;
  category: string;
  views: number | null;
  likes: number | null;
  comments: number | null;
  shares: number | null;
  engagement_rate: number | null;
  published_at: string | null;
};

export type DashboardTrendPoint = {
  date: string;
  views: number;
};

export type DashboardData = {
  data_source: "development" | "empty";
  creator: DashboardCreator | null;
  metrics: DashboardMetric[];
  performance_trend: DashboardTrendPoint[];
  best_performing_content: DashboardContent[];
  recent_content: DashboardContent[];
  insight: {
    title: string;
    summary: string;
    evidence: string | null;
    confidence: number | null;
    method: string | null;
  };
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchDashboard(creatorId: string = DEVELOPMENT_CREATOR_ID): Promise<DashboardData> {
  const response = await fetch(`${apiBaseUrl}/api/v1/dashboard?creator_id=${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Dashboard request failed with status ${response.status}`);
  }

  return (await response.json()) as DashboardData;
}
