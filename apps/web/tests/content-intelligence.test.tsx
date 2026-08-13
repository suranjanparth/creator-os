import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ContentIntelligencePage from "@/app/content-intelligence/page";
import { fetchContentIntelligence } from "@/features/content-intelligence/api";

vi.mock("@/features/content-intelligence/api", () => ({
  fetchContentIntelligence: vi.fn(),
}));

const mockedFetchContentIntelligence = vi.mocked(fetchContentIntelligence);

describe("ContentIntelligencePage", () => {
  beforeEach(() => {
    mockedFetchContentIntelligence.mockReset();
  });

  it("shows an explicit empty state when the API has no analyzed posts", async () => {
    mockedFetchContentIntelligence.mockResolvedValue({ data_source: "empty", method: "Rule based", summary: null, items: [] });

    render(<ContentIntelligencePage />);

    expect(await screen.findByRole("heading", { name: "No analyzed posts yet." })).toBeInTheDocument();
  });

  it("explains when posts cannot yet be compared by format", async () => {
    mockedFetchContentIntelligence.mockResolvedValue({
      data_source: "development",
      method: "Rule based",
      summary: {
        strongest_content_format: null,
        weakest_content_format: null,
        strongest_engagement_driver: null,
        recommended_content_direction: null,
      },
      items: [{
        content: {
          id: "post-1", title: "A tested post", platform: "Instagram", content_type: "Carousel", category: "Creative practice",
          views: 100, likes: 10, comments: 2, shares: 3, engagement_rate: 10, published_at: "2026-08-09",
        },
        performance_score: 79, performance_tier: "Strong", primary_reason: "Shares are above average.",
        detected_pattern: "Save-and-share framework", recommended_next_action: "Create a follow-up carousel.",
      }],
    });

    render(<ContentIntelligencePage />);

    expect(await screen.findByText(/More posts in the same format are needed/i)).toBeInTheDocument();
  });
});
