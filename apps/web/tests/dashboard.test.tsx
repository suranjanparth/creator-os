import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";
import { fetchDashboard, type DashboardData } from "@/features/dashboard/api";

vi.mock("@/features/dashboard/api", () => ({
  fetchDashboard: vi.fn(),
}));

const mockedFetchDashboard = vi.mocked(fetchDashboard);

const populatedDashboard: DashboardData = {
  data_source: "development",
  creator: {
    name: "Maya Chen",
    handle: "@mayamakes",
    niche: "Creative systems & solo business",
    audience: "Ambitious creatives, 24-34",
    followers: 84200,
  },
  metrics: [
    { label: "Total views", value: 398400, change: null, detail: null },
    { label: "Engagement rate", value: 9.2, change: null, detail: null },
    { label: "Total content", value: 6, change: null, detail: null },
  ],
  performance_trend: [
    { date: "2026-07-27", views: 52200 },
    { date: "2026-08-09", views: 124000 },
  ],
  best_performing_content: [
    {
      id: "p1",
      title: "The permission slip to work slower",
      platform: "Instagram",
      content_type: "Carousel",
      category: "Creative practice",
      views: 52200,
      likes: 3850,
      comments: 244,
      shares: 1406,
      engagement_rate: 10.5,
      published_at: "2026-07-27",
    },
  ],
  recent_content: [
    {
      id: "p2",
      title: "The 20-minute creative reset",
      platform: "Instagram",
      content_type: "Reel",
      category: "Creative systems",
      views: 124000,
      likes: 8400,
      comments: 526,
      shares: 2211,
      engagement_rate: 9.0,
      published_at: "2026-08-09",
    },
  ],
  insight: {
    title: "Carousels lead engagement",
    summary: "Carousel posts average 9.8% engagement across 2 posts, making them the strongest format to build on next.",
    evidence: "Based on 2 carousel posts across 6 posts.",
    confidence: 0.33,
    method: "Initial intelligence layer: deterministic format-performance rule.",
  },
};

const emptyDashboard: DashboardData = {
  data_source: "empty",
  creator: null,
  metrics: [],
  performance_trend: [],
  best_performing_content: [],
  recent_content: [],
  insight: {
    title: "Connect your creator data to unlock insights",
    summary: "Creator OS will surface performance patterns once content data is available.",
    evidence: null,
    confidence: null,
    method: null,
  },
};

describe("DashboardPage", () => {
  beforeEach(() => {
    mockedFetchDashboard.mockReset();
  });

  it("renders persisted API dashboard data", async () => {
    mockedFetchDashboard.mockResolvedValue(populatedDashboard);

    render(<DashboardPage />);

    expect(await screen.findByRole("heading", { name: /Welcome back, Maya/i })).toBeInTheDocument();
    expect(screen.getByText("Total views")).toBeInTheDocument();
    expect(screen.getByText("Carousels lead engagement")).toBeInTheDocument();
    expect(screen.getByText("The 20-minute creative reset")).toBeInTheDocument();
  });

  it("requests dashboard data for the persisted active creator", async () => {
    window.localStorage.setItem("creator-os.active-creator-id", "alex-rivera");
    mockedFetchDashboard.mockResolvedValue(emptyDashboard);

    render(<DashboardPage />);

    await waitFor(() => expect(mockedFetchDashboard).toHaveBeenCalledWith("alex-rivera"));
  });

  it("shows a loading state while the dashboard is loading", () => {
    mockedFetchDashboard.mockReturnValue(new Promise(() => {}));

    render(<DashboardPage />);

    expect(screen.getByText("Loading your creator intelligence.")).toBeInTheDocument();
  });

  it("shows an honest API error state", async () => {
    mockedFetchDashboard.mockRejectedValue(new Error("unavailable"));

    render(<DashboardPage />);

    expect(await screen.findByRole("alert")).toHaveTextContent("We couldn't load your dashboard.");
  });

  it("renders an honest empty-data state without invented metrics", async () => {
    mockedFetchDashboard.mockResolvedValue(emptyDashboard);

    render(<DashboardPage />);

    expect(await screen.findByText("No creator connected")).toBeInTheDocument();
    expect(screen.getByText("Connect your creator data to unlock insights")).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByText("Last 14 days")).not.toBeInTheDocument());
    expect(screen.queryByText(/18\.4%/)).not.toBeInTheDocument();
  });

  it("does not display fabricated change percentages or period claims when data is present", async () => {
    mockedFetchDashboard.mockResolvedValue(populatedDashboard);

    render(<DashboardPage />);

    await screen.findByRole("heading", { name: /Welcome back, Maya/i });

    expect(screen.getAllByText("Awaiting data").length).toBe(3);
    expect(screen.queryByText("Last 14 days")).not.toBeInTheDocument();
    expect(screen.queryByText(/\+18\.4%/)).not.toBeInTheDocument();
    expect(screen.queryByText("· Development dataset")).not.toBeInTheDocument();
  });
});
