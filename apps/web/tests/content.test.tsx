import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ContentPage from "@/app/content/page";
import { ingestContentBatch } from "@/features/content-ingest/api";
import { fetchContentIntelligence } from "@/features/content-intelligence/api";

vi.mock("@/features/content-intelligence/api", () => ({
  fetchContentIntelligence: vi.fn(),
}));

vi.mock("@/features/content-ingest/api", () => ({
  ingestContentBatch: vi.fn(),
}));

const mockedFetchContentIntelligence = vi.mocked(fetchContentIntelligence);
const mockedIngestContentBatch = vi.mocked(ingestContentBatch);

const item = {
  content: {
    id: "post-1",
    title: "A tested post",
    platform: "Instagram",
    content_type: "Carousel",
    category: "Creative practice",
    views: 100,
    likes: 10,
    comments: 2,
    shares: 3,
    engagement_rate: 10,
    published_at: "2026-08-09",
  },
  performance_score: 79,
  performance_tier: "Strong" as const,
  primary_reason: "Shares are above the seeded average.",
  detected_pattern: "Save-and-share framework",
  recommended_next_action: "Create a follow-up carousel using the same creative practice angle.",
};

describe("ContentPage", () => {
  beforeEach(() => {
    mockedFetchContentIntelligence.mockReset();
    mockedIngestContentBatch.mockReset();
    mockedFetchContentIntelligence.mockResolvedValue({ data_source: "development", method: "Rule based", summary: null, items: [item] });
  });

  it("renders an API-backed insight and applies its recommendation", async () => {
    render(<ContentPage />);

    expect(await screen.findByRole("heading", { name: "A tested post" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Generate angle/i }));

    expect(screen.getByLabelText("Content idea")).toHaveValue(item.recommended_next_action);
  });

  it("shows an honest error when intelligence cannot load", async () => {
    mockedFetchContentIntelligence.mockRejectedValue(new Error("unavailable"));

    render(<ContentPage />);

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Content Intelligence could not be reached"));
  });

  it("shows a loading state while intelligence is loading", () => {
    mockedFetchContentIntelligence.mockReturnValue(new Promise(() => {}));

    render(<ContentPage />);

    expect(screen.getByText("Loading analyzed posts...")).toBeInTheDocument();
  });

  it("shows an empty state when no analyzed posts are available", async () => {
    mockedFetchContentIntelligence.mockResolvedValue({ data_source: "empty", method: "Rule based", summary: null, items: [] });

    render(<ContentPage />);

    expect(await screen.findByText("No analyzed posts are available yet.")).toBeInTheDocument();
  });

  it("imports a JSON batch of published content with an honest success state", async () => {
    mockedIngestContentBatch.mockResolvedValue({
      creator_id: "maya-chen",
      received: 2,
      created: 2,
      skipped: 0,
      items: [
        { id: "post-1", status: "created", detail: null },
        { id: "post-2", status: "created", detail: null },
      ],
    });

    render(<ContentPage />);

    await screen.findByRole("heading", { name: "A tested post" });
    fireEvent.click(screen.getByRole("button", { name: /import/i }));
    fireEvent.change(
      screen.getByLabelText("Content JSON"),
      { target: { value: '[{"id":"post-1","platform":"Instagram","content_type":"Reel","category":"Creative practice","title":"One"},{"id":"post-2","platform":"LinkedIn","content_type":"Text post","category":"Solo business","title":"Two"}]' } },
    );
    fireEvent.click(screen.getByRole("button", { name: /import posts/i }));

    expect(await screen.findByText("2 imported · 0 skipped")).toBeInTheDocument();
    expect(mockedIngestContentBatch).toHaveBeenCalledWith("maya-chen", expect.any(Array));
  });

  it("shows a validation error for malformed import JSON", async () => {
    render(<ContentPage />);

    await screen.findByRole("heading", { name: "A tested post" });
    fireEvent.click(screen.getByRole("button", { name: /import/i }));
    fireEvent.change(screen.getByLabelText("Content JSON"), { target: { value: "not json" } });
    fireEvent.click(screen.getByRole("button", { name: /import posts/i }));

    expect(await screen.findByText(/Paste a valid JSON array/)).toBeInTheDocument();
    expect(mockedIngestContentBatch).not.toHaveBeenCalled();
  });

  it("shows an honest API error state when the ingest request fails", async () => {
    mockedIngestContentBatch.mockRejectedValue(new Error("unavailable"));

    render(<ContentPage />);

    await screen.findByRole("heading", { name: "A tested post" });
    fireEvent.click(screen.getByRole("button", { name: /import/i }));
    fireEvent.change(screen.getByLabelText("Content JSON"), { target: { value: "[{}]" } });
    fireEvent.click(screen.getByRole("button", { name: /import posts/i }));

    expect(await screen.findByText(/Import failed/)).toBeInTheDocument();
  });
});
