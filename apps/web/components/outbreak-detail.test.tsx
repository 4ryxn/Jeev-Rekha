import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiFetch, type Outbreak, type WeatherContext } from "@/lib/api";
import { OutbreakDetail } from "./outbreak-detail";

vi.mock("@/lib/api", () => ({ apiFetch: vi.fn() }));

const outbreak = {
  id: 7,
  disease_name: "Synthetic outbreak",
  species: "Cattle",
  status: "suspected",
  location_id: 3,
  data_source: "demo_seed",
  review_radius_km: null,
  detected_at: "2026-09-13T10:00:00Z",
  confirmed_at: null,
  suspected_cases: 4,
  confirmed_cases: 0,
  mortality_count: 0,
  verification_level: "reported",
  notes: null,
  created_at: "2026-09-13T10:00:00Z",
  location: {
    id: 3,
    name: "Haritpur",
    type: "village",
    location_type: "village",
    district: "Synthetic District",
    state: "Synthetic State",
    latitude: 18.52,
    longitude: 73.85,
    data_source: "demo_seed",
    is_active: true,
    created_at: "2026-09-13T10:00:00Z",
    updated_at: "2026-09-13T10:00:00Z",
  },
} as Outbreak;

const weather: WeatherContext = {
  available: true,
  message: null,
  observed_at: "2026-09-14T10:00:00Z",
  temperature_c: 27.5,
  relative_humidity: 71,
  wind_speed_kmh: 11.2,
  weather_code: 3,
  recent_days: [{ date: "2026-09-13", precipitation_mm: 2.4, temperature_max_c: 29, temperature_min_c: 21 }],
};

const apiFetchMock = vi.mocked(apiFetch);

beforeEach(() => {
  apiFetchMock.mockReset();
  apiFetchMock.mockImplementation((path: string) => path.includes("weather-context") ? Promise.resolve(weather) : Promise.resolve(outbreak));
});

describe("OutbreakDetail environmental context", () => {
  it("renders current weather and recent history", async () => {
    render(<OutbreakDetail outbreakId={7} />);

    expect(await screen.findByRole("heading", { name: "Current and recent weather" })).toBeTruthy();
    expect(screen.getByText("27.5°C")).toBeTruthy();
    expect(screen.getByText("2.4 mm")).toBeTruthy();
    expect(screen.getByText(/not a predictive or causal claim/)).toBeTruthy();
  });

  it("renders the unavailable fallback when weather loading fails", async () => {
    apiFetchMock.mockImplementation((path: string) => path.includes("weather-context") ? Promise.reject(new Error("Open-Meteo unavailable")) : Promise.resolve(outbreak));

    render(<OutbreakDetail outbreakId={7} />);

    expect(await screen.findByRole("heading", { name: "Weather data unavailable" })).toBeTruthy();
    expect(screen.getByText(/does not affect the outbreak record/)).toBeTruthy();
  });
});
