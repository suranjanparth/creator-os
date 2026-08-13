import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import CreatorDnaPage from "@/app/creator-dna/page";
import { fetchCreatorDna, type DnaData } from "@/features/dna/api";

vi.mock("@/features/dna/api", () => ({
  fetchCreatorDna: vi.fn(),
}));

const mockedFetchCreatorDna = vi.mocked(fetchCreatorDna);

const populatedDna: DnaData = {
  data_source: "development",
  identity: {
    name: "Maya Chen",
    handle: "@mayamakes",
    niche: "Creative systems & solo business",
    audience: "Ambitious creatives, 24-34",
    platform: "Instagram",
    follower_count: 84200,
  },
  total_posts: 6,
  platforms: [{ name: "Instagram", count: 3, share: 50.0 }],
  formats: [
    { name: "Carousel", count: 2, share: 33.3 },
    { name: "Reel", count: 1, share: 16.7 },
  ],
  categories: [{ name: "Creative systems", count: 3, share: 50.0 }],
  best_format: { name: "Carousel", average_engagement_rate: 9.8, sample_size: 2 },
  engagement_benchmark: { average_views: 66400.0, average_engagement_rate: 8.7, sample_size: 6 },
  insights: [
    {
      title: "Carousels lead your engagement",
      summary: "Carousel posts average 9.8% engagement across 2 posts.",
      evidence: "Based on 2 posts in this format.",
      sample_size: 2,
    },
  ],
};

const emptyDna: DnaData = {
  data_source: "empty",
  identity: null,
  total_posts: 0,
  platforms: [],
  formats: [],
  categories: [],
  best_format: null,
  engagement_benchmark: null,
  insights: [{ title: "No published content yet", summary: "Import or connect published content with performance data to map your creative pattern.", evidence: null, sample_size: 0 }],
};

describe("CreatorDnaPage", () => {
  beforeEach(() => {
    mockedFetchCreatorDna.mockReset();
  });

  it("renders the persisted creator identity and real content signals", async () => {
    mockedFetchCreatorDna.mockResolvedValue(populatedDna);

    render(<CreatorDnaPage />);

    await waitFor(() => expect(screen.getByText("Maya Chen")).toBeInTheDocument());
    expect(screen.getByText("@mayamakes · Creative systems & solo business")).toBeInTheDocument();
    expect(screen.getByText("Carousels lead your engagement")).toBeInTheDocument();
    expect(screen.getByText("6 posts analyzed")).toBeInTheDocument();
    expect(screen.getByText("Carousel · 9.8% engagement")).toBeInTheDocument();
    expect(screen.getByText("2 posts analyzed")).toBeInTheDocument();
  });

  it("renders an honest empty-data state without fabricated signals", async () => {
    mockedFetchCreatorDna.mockResolvedValue(emptyDna);

    render(<CreatorDnaPage />);

    await waitFor(() => expect(screen.getByText("No creator connected")).toBeInTheDocument());
    expect(screen.getByText("No published content yet")).toBeInTheDocument();
    expect(screen.getAllByText("0 posts analyzed").length).toBeGreaterThan(0);
  });

  it("shows an honest API error state", async () => {
    mockedFetchCreatorDna.mockRejectedValue(new Error("unavailable"));

    render(<CreatorDnaPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("We couldn't load your creator DNA."));
  });
});
