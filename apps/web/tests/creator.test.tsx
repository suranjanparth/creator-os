import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppNavigation } from "@/components/AppNavigation";
import { fetchCreatorProfile, fetchCreatorProfiles, type CreatorProfile } from "@/features/creator/api";

vi.mock("@/features/creator/api", () => ({
  fetchCreatorProfile: vi.fn(),
  fetchCreatorProfiles: vi.fn(),
}));

const mockedFetchCreatorProfile = vi.mocked(fetchCreatorProfile);
const mockedFetchCreatorProfiles = vi.mocked(fetchCreatorProfiles);

const profile: CreatorProfile = {
  creator_id: "maya-chen",
  name: "Maya Chen",
  handle: "@mayamakes",
  profile_url: "https://instagram.com/mayamakes",
  niche: "Creative systems & solo business",
  platform: "Instagram",
  audience: "Ambitious creatives, 24-34",
  follower_count: 84200,
  created_at: "2026-08-12T10:00:00",
  updated_at: "2026-08-12T10:00:00",
};

describe("AppNavigation", () => {
  beforeEach(() => {
    mockedFetchCreatorProfile.mockReset();
    mockedFetchCreatorProfiles.mockReset();
    mockedFetchCreatorProfiles.mockResolvedValue([profile]);
  });

  it("renders the persisted creator profile in the nav chip", async () => {
    window.localStorage.setItem("creator-os.active-creator-id", "maya-chen");
    mockedFetchCreatorProfile.mockResolvedValue(profile);

    render(<AppNavigation />);

    await waitFor(() => expect(mockedFetchCreatorProfile).toHaveBeenCalledWith("maya-chen"));
    expect(screen.getByText("Maya Chen")).toBeInTheDocument();
    expect(screen.getByText("@mayamakes")).toBeInTheDocument();
    expect(screen.getByText("MC")).toBeInTheDocument();
  });

  it("loads the profile for the persisted active creator", async () => {
    window.localStorage.setItem("creator-os.active-creator-id", "alex-rivera");
    mockedFetchCreatorProfile.mockResolvedValue({ ...profile, creator_id: "alex-rivera", name: "Alex Rivera", handle: "@alexmakes" });

    render(<AppNavigation />);

    await waitFor(() => expect(mockedFetchCreatorProfile).toHaveBeenCalledWith("alex-rivera"));
    expect(screen.getByText("Alex Rivera", { selector: "strong" })).toBeInTheDocument();
  });

  it("lets the user switch to another persisted creator", async () => {
    const alex = { ...profile, creator_id: "alex-rivera", name: "Alex Rivera", handle: "@alexmakes" };
    mockedFetchCreatorProfiles.mockResolvedValue([profile, alex]);
    mockedFetchCreatorProfile.mockImplementation(async (creatorId) => creatorId === "alex-rivera" ? alex : profile);

    render(<AppNavigation />);

    await screen.findByRole("combobox", { name: "Active creator" });
    fireEvent.change(screen.getByRole("combobox", { name: "Active creator" }), { target: { value: "alex-rivera" } });

    await waitFor(() => expect(mockedFetchCreatorProfile).toHaveBeenCalledWith("alex-rivera"));
    expect(window.localStorage.getItem("creator-os.active-creator-id")).toBe("alex-rivera");
    expect(screen.getByText("Alex Rivera", { selector: "strong" })).toBeInTheDocument();
  });

  it("shows an honest loading fallback while the profile is fetching", () => {
    mockedFetchCreatorProfile.mockReturnValue(new Promise(() => {}));
    mockedFetchCreatorProfiles.mockReturnValue(new Promise(() => {}));

    render(<AppNavigation />);

    expect(screen.getByText("Loading profile…")).toBeInTheDocument();
  });

  it("shows an honest unavailable fallback when the profile cannot be reached", async () => {
    window.localStorage.setItem("creator-os.active-creator-id", "maya-chen");
    mockedFetchCreatorProfile.mockRejectedValue(new Error("unavailable"));

    render(<AppNavigation />);

    await waitFor(() => expect(screen.getByText("Profile unavailable")).toBeInTheDocument());
  });
});
