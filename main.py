import asyncio
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

    root = RootAgentAsync(planner=planner, llm=llm, weather_service=weather_service, osm_service=osm_service)

    print("AI Trail Buddy (async) is ready! Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            break
        response = await root.handle_message(user_input)
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
