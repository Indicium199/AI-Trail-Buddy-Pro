import re
import asyncio
import logging
from trail_buddy.agents.llm_agent import LlmAgent
from trail_buddy.planner.trail_planner import PlannerAgent
from trail_buddy.services.weather_service import WeatherService
from trail_buddy.services.osm_service import OsmService

logger = logging.getLogger(__name__)

class RootAgentAsync:
    """Async orchestrator for Trail Buddy with Gemini-powered summaries."""

    SCENERY_SYNONYMS = {
        "scenic": ["panoramic", "lake", "forest", "view", "fell", "mountain", "scenic"],
        "water": ["lake", "river", "stream", "waterfall", "pond"],
        "mountain": ["fell", "peak", "ridge", "mountain"],
        "forest": ["woodland", "forest", "trees"],
        "lake": ["lake", "water", "pond"],
        "panoramic": ["panoramic", "view", "scenic"],
        "relaxing": ["peaceful", "quiet", "relaxing"]
    }

    def __init__(self, planner: PlannerAgent, llm: LlmAgent, weather_service: WeatherService, osm_service: OsmService):
        self.planner = planner
        self.llm = llm
        self.weather_service = weather_service
        self.osm_service = osm_service

        # Conversation state
        self.state = {
            "awaiting_input": "difficulty",
            "difficulty": None,
            "max_distance": None,
            "scenery": None,
            "route_type": None,
            "selected_trail": None
        }

    def filter_trails_by_scenery(self, trails, scenery_input):
        """Soft filter trails by scenery synonyms."""
        if not scenery_input:
            return trails
        keywords = []
        for kw in re.findall(r'\w+', scenery_input.lower()):
            keywords.extend(self.SCENERY_SYNONYMS.get(kw, [kw]))
        filtered = []
        for trail in trails:
            tags = trail.get("Tags", [])
            if isinstance(tags, str):
                tags = [tags]
            trail_text = " ".join(tags).lower()
            if any(k in trail_text for k in keywords):
                filtered.append(trail)
        return filtered if filtered else trails

    async def handle_message(self, msg: str):
        msg_lower = msg.strip().lower()

        # --- Difficulty ---
        if self.state["awaiting_input"] == "difficulty":
            for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                if level in msg_lower:
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"
                    return "Max distance (km)?"
            return "Choose difficulty: Very Easy, Easy, Moderate, Hard, Very Hard"

        # --- Max distance ---
        if self.state["awaiting_input"] == "max_distance":
            try:
                self.state["max_distance"] = float(msg)
                self.state["awaiting_input"] = "scenery"
                return "Preferred scenery? (Lake, Forest, Panoramic, etc. — optional)"
            except ValueError:
                return "Please enter a number."

        # --- Scenery ---
        if self.state["awaiting_input"] == "scenery":
            self.state["scenery"] = msg.strip() if msg.strip() else None
            self.state["awaiting_input"] = "route_type"
            return "Preferred route type? (Loop, Out-and-back, Ridge)"

        # --- Route type and trail selection ---
        if self.state["awaiting_input"] == "route_type":
            self.state["route_type"] = msg.strip() if msg.strip() else None

            # Filter trails
            trails = self.planner.filter_trails(
                difficulty=self.state["difficulty"],
                max_distance=self.state["max_distance"],
                route_type=self.state["route_type"],
                soft_distance=True
            )
            trails = self.filter_trails_by_scenery(trails, self.state["scenery"])
            if not trails:
                self.state["awaiting_input"] = None
                return "Sorry, I couldn’t find any trails matching your preferences."

            # Select first trail (simple default)
            selected = trails[0]
            self.state["selected_trail"] = selected

            # Gemini prompt for trail description
            prompt = (
                f"You are a friendly hiking guide. "
                f"Recommend this trail in a cheerful paragraph:\n\n"
                f"Name: {selected['Trail']}\n"
                f"Difficulty: {selected['Difficulty']}\n"
                f"Distance: {selected['Distance_km']} km\n"
                f"Route: {selected.get('Route','N/A')}\n"
                f"Tags: {selected.get('Tags','')}"
            )
            description = await asyncio.to_thread(self.llm.ask_gemini, prompt)
            if not description:
                description = f"{selected['Trail']} is a {selected['Difficulty']} trail, {selected['Distance_km']} km long."

            self.state["awaiting_input"] = "confirm_weather"
            return f"{description}\n\nWould you like the current weather for this trail?"

        # --- Weather ---
        if self.state["awaiting_input"] == "confirm_weather":
            trail = self.state["selected_trail"]
            lat, lon = trail.get("Lat"), trail.get("Lng")
            if msg_lower in ["yes", "y"]:
                weather = await self.weather_service.get_weather(lat, lon)
                weather_desc = await self.weather_service.map_weather_code(weather["weather_code"])

                # Gemini summary for weather
                weather_prompt = (
                    f"You are a friendly hiking assistant. "
                    f"Provide a short, cheerful summary of the current weather at {trail['Trail']} for hikers:\n"
                    f"Temperature: {weather['temperature']}°C\n"
                    f"Windspeed: {weather['windspeed']} km/h\n"
                    f"Condition: {weather_desc}"
                )
                weather_msg = await asyncio.to_thread(self.llm.ask_gemini, weather_prompt)

                self.state["awaiting_input"] = "confirm_pubs"
                return f"{weather_msg}\n\nWould you like me to find cafes or pubs nearby?"
            else:
                self.state["awaiting_input"] = "confirm_pubs"
                return "No problem! Would you like me to find cafes or pubs nearby?"

        # --- Pubs / Cafes ---
        if self.state["awaiting_input"] == "confirm_pubs":
            trail = self.state["selected_trail"]
            lat, lon = trail.get("Lat"), trail.get("Lng")
            if msg_lower in ["yes", "y", "pubs", "cafes", "cafe", "pub"]:
                if msg_lower in ["pub", "pubs"]:
                    place_types = ["pub"]
                elif msg_lower in ["cafe", "cafes"]:
                    place_types = ["cafe"]
                else:
                    place_types = ["cafe", "pub"]

                places = await self.osm_service.get_nearby_places(lat, lon, radius=20000, place_types=place_types)
                if places:
                    formatted = [f"{i+1}. {p['name']} – {p.get('distance_km','?')} km away"
                                 for i, p in enumerate(places)]
                    places_text = "\n".join(formatted)

                    # Gemini summary for pubs/cafes
                    places_prompt = (
                        f"You are a friendly hiking assistant. "
                        f"Here is a list of nearby {', '.join(place_types)} for the trail {trail['Trail']}:\n"
                        f"{places_text}\n"
                        "Please summarize this in 2–3 cheerful sentences highlighting good options and distances."
                    )
                    places_summary = await asyncio.to_thread(self.llm.ask_gemini, places_prompt)
                    self.state["awaiting_input"] = None
                    return places_summary
                else:
                    self.state["awaiting_input"] = None
                    return f"Sorry, no nearby {', '.join(place_types)} found within 20 km."
            else:
                self.state["awaiting_input"] = None
                return "Alright! Enjoy your hike! 🌄"

        # --- Fallback ---
        return "I'm not sure how to respond. Please follow the prompts."
