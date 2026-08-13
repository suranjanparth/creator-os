import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ConnectPage from "@/app/connect/page";
import { importCreator, type CreatorImportResult } from "@/features/ingestion/api";

vi.mock("@/features/ingestion/api", () => ({
  importCreator: vi.fn(),
}));

const mockedImportCreator = vi.mocked(importCreator);

const importResult: CreatorImportResult = {
  creator_id: "maya-chen",
  profile_status: "created",
  content_received: 2,
  created: 2,
  updated: 0,
  skipped: 0,
  errors: 0,
  items: [
    { id: "post-1", status: "created", detail: null },
    { id: "post-2", status: "created", detail: null },
  ],
};

const alexImportResult: CreatorImportResult = {
  ...importResult,
  creator_id: "alex-rivera",
};

const validPayload = `{
  "profile": { "name": "Maya Chen", "handle": "@mayamakes", "platform": "Instagram", "follower_count": 84200 },
  "content": [
    { "id": "post-1", "platform": "Instagram", "content_type": "Reel", "category": "Creative systems", "title": "A reel", "views": 12000 },
    { "id": "post-2", "platform": "Instagram", "content_type": "Carousel", "category": "Creative practice", "title": "A carousel" }
  ]
}`;

function setPayload(value: string) {
  fireEvent.change(screen.getByLabelText("Creator payload (JSON)"), { target: { value } });
}

describe("ConnectPage", () => {
  beforeEach(() => {
    mockedImportCreator.mockReset();
  });

  it("describes the future authorized-account flow without claiming it is live", () => {
    render(<ConnectPage />);

    expect(screen.getByText("Authorize your Instagram")).toBeInTheDocument();
    expect(screen.getByText("Development import")).toBeInTheDocument();
    expect(screen.queryByText(/OAuth successful/i)).not.toBeInTheDocument();
  });

  it("shows an empty state when there is nothing to import", () => {
    render(<ConnectPage />);

    setPayload("");
    expect(screen.getByText(/Nothing to import yet/)).toBeInTheDocument();
  });

  it("imports a creator payload and shows the success report", async () => {
    mockedImportCreator.mockResolvedValue(importResult);

    render(<ConnectPage />);

    setPayload(validPayload);
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    expect(await screen.findByRole("status", { name: "Import result" })).toBeInTheDocument();
    expect(mockedImportCreator).toHaveBeenCalledWith(
      expect.objectContaining({ creator_id: "maya-chen", profile: expect.objectContaining({ name: "Maya Chen" }) }),
    );
    expect(screen.getByText("Import report")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open dashboard/ })).toBeInTheDocument();
  });

  it("makes a successfully imported creator the active creator", async () => {
    mockedImportCreator.mockResolvedValue(alexImportResult);

    render(<ConnectPage />);

    fireEvent.change(screen.getByLabelText("Creator ID"), { target: { value: "alex-rivera" } });
    setPayload(validPayload);
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    await screen.findByRole("status", { name: "Import result" });
    expect(window.localStorage.getItem("creator-os.active-creator-id")).toBe("alex-rivera");
  });

  it("shows a loading state while the import is in flight", () => {
    mockedImportCreator.mockReturnValue(new Promise(() => {}));

    render(<ConnectPage />);

    setPayload(validPayload);
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    expect(screen.getByText("Importing creator data...")).toBeInTheDocument();
  });

  it("shows a validation error for malformed JSON", () => {
    render(<ConnectPage />);

    setPayload("{ not json");
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    expect(screen.getByText("Paste valid JSON before importing.")).toBeInTheDocument();
  });

  it("shows a validation error when the profile object is missing", () => {
    render(<ConnectPage />);

    setPayload('{ "content": [] }');
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    expect(screen.getByText(/must include a "profile" object/)).toBeInTheDocument();
  });

  it("shows an error state when the import request fails", async () => {
    mockedImportCreator.mockRejectedValue(new Error("Creator import request failed with status 503"));

    render(<ConnectPage />);

    setPayload(validPayload);
    fireEvent.click(screen.getByRole("button", { name: /Import creator data/ }));

    expect(await screen.findByText("Creator import request failed with status 503")).toBeInTheDocument();
  });
});
