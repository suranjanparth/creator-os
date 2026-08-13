import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import AnalyticsPage from "@/app/analytics/page";
import { fetchAnalytics, type AnalyticsData } from "@/features/analytics/api";

vi.mock("@/features/analytics/api", () => ({
  fetchAnalytics: vi.fn(),
}));

const mockedFetchAnalytics = vi.mocked(fetchAnalytics);

const populatedAnalytics: AnalyticsData = {
  data_source: "development",
  total_posts: 6,
  totals: {
    views: 398400,
    likes: 27030,
    comments: 2183,
    shares: 7604,
    engagements: 36817,
    average_engagement_rate: 9.0,
  },
  platform_breakdown: [
    { platform: "Instagram", posts: 3, views: 243200, share: 61.0 },
    { platform: "TikTok", posts: 1, views: 91000, share: 22.8 },
  ],
  top_posts: [
    {
      id: "post-1",
      title: "The 20-minute creative reset",
      platform: "Instagram",
      content_type: "Reel",
      views: 124000,
      engagement_rate: 9.0,
      published_at: "2026-08-09",
    },
  ],
  trend: [
    { date: "2026-07-27", views: 52200 },
    { date: "2026-08-09", views: 124000 },
  ],
  engagement_anatomy: { likes_share: 73.4, comments_share: 5.9, shares_share: 20.7, sample_size: 6 },
};

const emptyAnalytics: AnalyticsData = {
  data_source: "empty",
  total_posts: 0,
  totals: null,
  platform_breakdown: [],
  top_posts: [],
  trend: [],
  engagement_anatomy: null,
};

describe("AnalyticsPage", () => {
  beforeEach(() => {
    mockedFetchAnalytics.mockReset();
  });

  it("renders analytics derived from persisted content", async () => {
    mockedFetchAnalytics.mockResolvedValue(populatedAnalytics);

    render(<AnalyticsPage />);

    await waitFor(() => expect(screen.getByText("Total views")).toBeInTheDocument());
    expect(screen.getByText("398.4K")).toBeInTheDocument();
    expect(screen.getAllByText("9.0%").length).toBeGreaterThan(0);
    expect(screen.getByText("6 posts analyzed")).toBeInTheDocument();
    expect(screen.getAllByText("The 20-minute creative reset").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Instagram").length).toBeGreaterThan(0);
    expect(screen.getByText("61%")).toBeInTheDocument();
    expect(screen.getByText(/73\.4/)).toBeInTheDocument();
  });

  it("renders an honest empty-data state without fabricated numbers", async () => {
    mockedFetchAnalytics.mockResolvedValue(emptyAnalytics);

    render(<AnalyticsPage />);

    await waitFor(() => expect(screen.getByText("No published content to analyze yet.")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /import content/i })).toHaveAttribute("href", "/content");
    expect(screen.queryByText("Total views")).not.toBeInTheDocument();
  });

  it("shows an honest API error state", async () => {
    mockedFetchAnalytics.mockRejectedValue(new Error("unavailable"));

    render(<AnalyticsPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("We couldn't load your analytics."));
  });
});
