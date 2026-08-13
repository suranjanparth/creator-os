import { afterEach, describe, expect, it, vi } from "vitest";

import { importCreator, type CreatorImportPayload } from "@/features/ingestion/api";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const payload: CreatorImportPayload = {
  creator_id: "alex-rivera",
  profile: { name: "Alex Rivera", handle: "@alexmakes", platform: "Instagram", follower_count: 1200 },
  content: [
    {
      id: "ar-1",
      platform: "Instagram",
      content_type: "Reel",
      category: "Creative systems",
      title: "First reel",
      views: 5000,
    },
  ],
};

describe("importCreator", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("POSTs a normalized creator payload to the ingestion endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ creator_id: "alex-rivera" }) });
    vi.stubGlobal("fetch", fetchMock);

    await importCreator(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      `${apiBaseUrl}/api/v1/ingestion/import`,
      expect.objectContaining({ method: "POST" }),
    );
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(JSON.parse(String(init.body))).toEqual(payload);
  });

  it("throws a descriptive error for an API failure status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: "Profile is required" }) }));

    await expect(importCreator(payload)).rejects.toThrow("Profile is required");
  });

  it("surfaces the HTTP status when the response body is not JSON", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => { throw new Error("not json"); } }));

    await expect(importCreator(payload)).rejects.toThrow("Creator import request failed with status 503");
  });
});
