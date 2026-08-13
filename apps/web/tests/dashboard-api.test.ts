import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchDashboard } from "@/features/dashboard/api";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function okResponse(payload: unknown) {
  return vi.fn().mockResolvedValue({ ok: true, json: async () => payload });
}

describe("fetchDashboard", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("requests the scoped dashboard endpoint for the development creator", async () => {
    const fetchMock = okResponse({ data_source: "empty" });
    vi.stubGlobal("fetch", fetchMock);

    await fetchDashboard();

    expect(fetchMock).toHaveBeenCalledWith(`${apiBaseUrl}/api/v1/dashboard?creator_id=maya-chen`);
  });

  it("encodes a custom creator id in the query string", async () => {
    const fetchMock = okResponse({ data_source: "empty" });
    vi.stubGlobal("fetch", fetchMock);

    await fetchDashboard("some creator");

    expect(fetchMock).toHaveBeenCalledWith(`${apiBaseUrl}/api/v1/dashboard?creator_id=some%20creator`);
  });

  it("throws a descriptive error when the backend responds with a failure status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503 }));

    await expect(fetchDashboard()).rejects.toThrow("Dashboard request failed with status 503");
  });
});
