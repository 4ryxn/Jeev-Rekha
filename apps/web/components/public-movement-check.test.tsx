import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({ apiFetch: vi.fn(() => new Promise(() => undefined)) }));
import { PublicMovementCheckPage } from "./public-movement-check";

describe("PublicMovementCheckPage language toggle", () => {
  it("switches the rendered title to Hindi", () => {
    render(<PublicMovementCheckPage />);
    expect(screen.getByRole("heading", { name: /Pre-Travel Animal Movement Check/i })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "हिन्दी" }));
    expect(screen.getByRole("heading", { name: "जीव रेखा — यात्रा-पूर्व पशु आवागमन जाँच" })).toBeTruthy();
  });
});
