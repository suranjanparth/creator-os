import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders the CREATOR OS foundation message", () => {
    render(<HomePage />);

    expect(screen.getByRole("heading", { name: "CREATOR OS" })).toBeInTheDocument();
    expect(screen.getByText("Frontend foundation is running.")).toBeInTheDocument();
  });
});
