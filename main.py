import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os

# ---------------------------
# Logging Setup
# ---------------------------

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# 1. File handler — stores full logs (DEBUG and up)
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=1_000_000, backupCount=3
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

# 2. Console handler — show only warnings & errors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter(
    "%(levelname)s: %(message)s"
))

# 3. Configure root logger
logging.basicConfig(
    level=logging.DEBUG,     # ensures file log gets everything
    handlers=[file_handler, console_handler]
)

# Reduce noise from noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("trail_buddy").setLevel(logging.WARNING)

# ---------------------------
# Your Trail Buddy Code
# ---------------------------

from trail_buddy.agents.root_agent import RootAgentAsync
from trail_buddy.agents.llm_agent import LlmAgent
from trail_buddy.planner.trail_planner import PlannerAgent
from trail_buddy.services.weather_service import WeatherService
from trail_buddy.services.osm_service import OsmService

async def main():
    planner = PlannerAgent()
    weather_service = WeatherService()
    osm_service = OsmService()
    llm = LlmAgent()  # Local Gemini API key used here

    root = RootAgentAsync(
        planner=planner,
        llm=llm,
        weather_service=weather_service,
        osm_service=osm_service
    )

    print("AI Trail Buddy (async) is ready! Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        response = await root.handle_message(user_input)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())

