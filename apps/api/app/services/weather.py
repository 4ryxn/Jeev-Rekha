"""Read-only Open-Meteo environmental context for a persisted outbreak location."""

import httpx

from app.models import Outbreak


class WeatherService:
    endpoint = "https://api.open-meteo.com/v1/forecast"

    def context_for(self, outbreak: Outbreak) -> dict[str, object]:
        try:
            response = httpx.get(
                self.endpoint,
                params={
                    "latitude": outbreak.location.latitude,
                    "longitude": outbreak.location.longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "past_days": 6,
                    "forecast_days": 1,
                    "timezone": "auto",
                },
                timeout=5.0,
            )
            response.raise_for_status()
            data = response.json()
            current, daily = data["current"], data["daily"]
            recent_days = [{"date": date, "precipitation_mm": precipitation, "temperature_max_c": maximum, "temperature_min_c": minimum} for date, precipitation, maximum, minimum in zip(daily["time"], daily["precipitation_sum"], daily["temperature_2m_max"], daily["temperature_2m_min"], strict=True)]
            return {"available": True, "observed_at": current["time"], "temperature_c": current["temperature_2m"], "relative_humidity": current["relative_humidity_2m"], "wind_speed_kmh": current["wind_speed_10m"], "weather_code": current["weather_code"], "recent_days": recent_days}
        except (httpx.HTTPError, KeyError, TypeError, ValueError):
            return {"available": False, "message": "Weather data unavailable.", "recent_days": []}
