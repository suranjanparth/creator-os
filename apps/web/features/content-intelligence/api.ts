import type { DashboardContent } from "@/features/dashboard/api";
import { DEVELOPMENT_CREATOR_ID } from "@/features/creator/scope";

export type PerformanceTier = "Excellent" | "Strong" | "Average" | "Weak";

export type ContentIntelligenceItem = {
  content: DashboardContent;
  performance_score: number;
  performance_tier: PerformanceTier;
  primary_reason: string;
  detected_pattern: string;
  recommended_next_action: string;
};

export type ContentIntelligenceData = {
  data_source: "development" | "empty";
  method: string;
  summary: {
    strongest_content_format: { name: string; average_score: number; sample_size: number } | null;
    weakest_content_format: { name: string; average_score: number; sample_size: number } | null;
    strongest_engagement_driver: string | null;
    recommended_content_direction: string | null;
  } | null;
  items: ContentIntelligenceItem[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchContentIntelligence(creatorId: string = DEVELOPMENT_CREATOR_ID): Promise<ContentIntelligenceData> {
  const response = await fetch(`${apiBaseUrl}/api/v1/content-intelligence?creator_id=${encodeURIComponent(creatorId)}`);

  if (!response.ok) {
    throw new Error(`Content intelligence request failed with status ${response.status}`);
  }

  return (await response.json()) as ContentIntelligenceData;
}
