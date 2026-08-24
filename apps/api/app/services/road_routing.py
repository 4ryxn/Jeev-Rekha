"""Small OSRM-compatible adapter; never exposes provider payloads to clients."""
from dataclasses import dataclass
import httpx

from app.core.config import get_settings

@dataclass
class RoadRoute:
    geometry: list[list[float]]
    distance_km: float
    minutes: int
    provider: str

class RoadRoutingProvider:
    def route(self, origin: tuple[float, float], destination: tuple[float, float]) -> RoadRoute:
        base = get_settings().routing_provider_base_url.rstrip("/")
        url = f"{base}/route/v1/driving/{origin[0]},{origin[1]};{destination[0]},{destination[1]}"
        try:
            response = httpx.get(url, params={"overview": "full", "geometries": "geojson"}, timeout=5.0)
            response.raise_for_status(); data = response.json(); route = data.get("routes", [None])[0]
            coordinates = route and route.get("geometry", {}).get("coordinates")
            if not coordinates or not isinstance(coordinates, list): raise ValueError("invalid route geometry")
            return RoadRoute(geometry=[[float(x), float(y)] for x, y in coordinates], distance_km=round(float(route["distance"])/1000, 1), minutes=max(1, round(float(route["duration"])/60)), provider=base)
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as error:
            raise RuntimeError("Road route provider is unavailable") from error
