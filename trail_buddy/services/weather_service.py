import httpx
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Async weather service using Open-Meteo API."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    async def get_weather(self, lat: float, lon: float) -> dict:
        """Fetch current weather for a location."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(self.BASE_URL, params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True
                })
                resp.raise_for_status()
                data = resp.json().get("current_weather", {})
                return {
                    "temperature": data.get("temperature", "?"),
                    "windspeed": data.get("windspeed", "?"),
                    "weather_code": data.get("weathercode", 0)
                }
            except Exception as e:
                logger.error("Weather API error: %s", e)
                return {"temperature": "?", "windspeed": "?", "weather_code": 0}

    async def map_weather_code(self, code: int) -> str:
        """Map weather code to human-readable description."""
        mapping = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Snow",
            73: "Snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Rain showers",
            82: "Rain showers"
        }
        return mapping.get(code, "Unknown weather")
