import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppNavigation } from "@/components/AppNavigation";
import { fetchCreatorProfile, fetchCreatorProfiles } from "@/features/creator/api";

vi.mock("@/features/creator/api", () => ({
  fetchCreatorProfile: vi.fn(),
  fetchCreatorProfiles: vi.fn(),
}));

const mockedFetchCreatorProfile = vi.mocked(fetchCreatorProfile);
const mockedFetchCreatorProfiles = vi.mocked(fetchCreatorProfiles);

const navigationLabels = ["Dashboard", "Content", "Intelligence", "Analytics", "Creator DNA", "Recommendations", "Connect"];

describe("AppNavigation", () => {
  beforeEach(() => {
    mockedFetchCreatorProfile.mockReturnValue(new Promise(() => {}));
    mockedFetchCreatorProfiles.mockReturnValue(new Promise(() => {}));
  });

  it("renders each navigation item as its own distinct link", () => {
    render(<AppNavigation />);

    const links = screen.getAllByRole("link");
    for (const label of navigationLabels) {
      expect(links.some((link) => link.textContent?.trim() === label)).toBe(true);
    }
  });

  it("keeps the navigation links inside a single spaced container", () => {
    render(<AppNavigation />);

    const navLinks = document.querySelector(".nav-links");
    expect(navLinks).not.toBeNull();
    expect(navLinks?.querySelectorAll("a")).toHaveLength(navigationLabels.length);
  });

  it("renders the brand separately from the profile chip", () => {
    render(<AppNavigation />);

    const brand = document.querySelector(".brand");
    const chip = document.querySelector(".profile-chip");
    expect(brand).not.toBeNull();
    expect(chip).not.toBeNull();
    expect(brand).not.toBe(chip);
    expect(screen.getByRole("link", { name: /CREATOR\s*OS/i })).toBeInTheDocument();
  });
});
