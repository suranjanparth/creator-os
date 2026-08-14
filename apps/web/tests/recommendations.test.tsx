import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import RecommendationsPage from "@/app/recommendations/page";
import { fetchRecommendations, type RecommendationsData } from "@/features/recommendations/api";

vi.mock("@/features/recommendations/api", () => ({
  fetchRecommendations: vi.fn(),
}));

const mockedFetchRecommendations = vi.mocked(fetchRecommendations);

const populatedRecommendations: RecommendationsData = {
  data_source: "development",
  priority_signal: "Carousels are your strongest format",
  priority_copy: "Carousel posts average 9.8% engagement across 2 posts — build on what already works.",
  recommendations: [
    {
      tag: "Post next",
      title: "Create a carousel around creative systems topics",
      description: "Open with the tension your creative systems audience responds to.",
      evidence: "Carousel posts average 9.8% engagement across 2 posts.",
      sample_size: 2,
      action: "Create content",
      href: "/content",
    },
  ],
  opportunities: [
    { title: "Explore creative systems topics", description: "Creative systems is your most-published topic.", href: "/content" },
  ],
  total_posts: 6,
};

const emptyRecommendations: RecommendationsData = {
  data_source: "empty",
  priority_signal: "Connect your content to unlock recommendations",
  priority_copy: "Creator OS will recommend next moves once published content with performance data is available.",
  recommendations: [],
  opportunities: [],
  total_posts: 0,
};

describe("RecommendationsPage", () => {
  beforeEach(() => {
    mockedFetchRecommendations.mockReset();
    window.localStorage.setItem("creator-os.active-creator-id", "maya-chen");
  });

  it("renders evidence-backed recommendations from persisted content", async () => {
    mockedFetchRecommendations.mockResolvedValue(populatedRecommendations);

    render(<RecommendationsPage />);

    await waitFor(() => expect(screen.getByText("Carousels are your strongest format")).toBeInTheDocument());
    expect(screen.getByText("Create a carousel around creative systems topics")).toBeInTheDocument();
    expect(screen.getByText("Carousel posts average 9.8% engagement across 2 posts.")).toBeInTheDocument();
    expect(screen.getByText("2 posts")).toBeInTheDocument();
    expect(screen.getByText("6 posts analyzed")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /create content/i })).toHaveAttribute("href", "/content");
  });

  it("renders an honest empty-data state without invented next moves", async () => {
    mockedFetchRecommendations.mockResolvedValue(emptyRecommendations);

    render(<RecommendationsPage />);

    await waitFor(() => expect(screen.getByText("Not enough content to recommend next moves yet.")).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /import content/i })).toHaveAttribute("href", "/content");
  });

  it("shows an honest API error state", async () => {
    mockedFetchRecommendations.mockRejectedValue(new Error("unavailable"));

    render(<RecommendationsPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("We couldn't load your recommendations."));
  });
});
