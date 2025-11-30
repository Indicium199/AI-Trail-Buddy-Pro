import httpx
import math
import logging

logger = logging.getLogger(__name__)

class OsmService:
    """Async service to find nearby places via Overpass API."""

    BASE_URL = "https://overpass-api.de/api/interpreter"

    async def get_nearby_places(self, lat: float, lon: float, radius: int = 20000, place_types=None):
        if place_types is None:
            place_types = ["cafe", "pub"]

        try:
            query = f"""
            [out:json];
            (
            {"".join([f'node["amenity"="{pt}"](around:{radius},{lat},{lon});' for pt in place_types])}
            );
            out center;
            """
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.BASE_URL, data=query)
                resp.raise_for_status()
                data = resp.json()

            places = []
            for elem in data.get("elements", []):
                plat = float(elem.get("lat", 0))
                plon = float(elem.get("lon", 0))
                distance = round(self.haversine(lat, lon, plat, plon), 2)
                places.append({
                    "name": elem.get("tags", {}).get("name", "Unknown"),
                    "lat": plat,
                    "lon": plon,
                    "distance_km": distance
                })
            return places
        except Exception as e:
            logger.error("OSM API error: %s", e)
            return []

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """Calculate distance in km between two lat/lon points."""
        # Ensure all are floats
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
        R = 6371.0  # Earth radius km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
