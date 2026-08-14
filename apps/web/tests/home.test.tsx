import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import HomePage from "@/app/page";
import { fetchCreatorProfiles } from "@/features/creator/api";

vi.mock("@/features/creator/api", () => ({
  fetchCreatorProfiles: vi.fn(),
}));

const mockedFetchCreatorProfiles = vi.mocked(fetchCreatorProfiles);

describe("HomePage", () => {
  beforeEach(() => {
    mockedFetchCreatorProfiles.mockReset();
  });

  it("renders the CREATOR OS foundation message", async () => {
    mockedFetchCreatorProfiles.mockResolvedValue([]);

    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "CREATOR OS" })).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("You don't have any creators yet.")).toBeInTheDocument());
  });
});
