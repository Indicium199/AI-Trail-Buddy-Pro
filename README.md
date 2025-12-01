# AI Trail Buddy Pro

**AI Trail Buddy Pro** is an AI-powered hiking assistant that helps users find and explore Lake District trails based on their preferences. It leverages a multi-agent system, LLM reasoning, and real-world APIs to provide personalized trail recommendations, weather updates, and pubs and cafes for a post hike refuel!

## Project Authorship and AI Assistance

AI Trail Buddy Pro was conceived, designed, and built by me. I chose the APIs, designed the multi-agent architecture, and orchestrated the workflow. AI was used as a tool to assist with code generation and text summaries, but all system design decisions and feature implementations are my own.

---

## Features

- **Multi-Agent Architecture**  
  - **LLM Agent:** Generates cheerful trail descriptions and reasoning using Google Gemini API.  
  - **Planner Agent:** Filters trails based on difficulty, distance, route type, and scenery.  
  - **Async Services:** Fetch current weather (Open-Meteo API) and nearby cafes/pubs (OSM Overpass API).  

- **Personalized Trail Recommendations**  
  - Input difficulty, distance, scenery preferences, and route type.  
  - Soft filtering using synonyms for scenery types.  

- **Friendly LLM-Generated Summaries**  
  - Generates natural language descriptions for trails and weather.  
  - Provides reasoning for trail selections via `TrailReasoner`.  

- **Async Multi-Step Conversations**  
  - Maintains conversation state across multiple user interactions.  
  - Handles sequential steps: difficulty → distance → scenery → route → weather → amenities.

- **Observability & Logging**  
  - Detailed logging of system events and errors.  
  - Rotating logs stored in `logs/app.log`.  

---

## Requirements

- Python 3.11+
- Dependencies (install via `pip install -r requirements.txt`):
  - `httpx`
  - `google-genai`
  - `python-dotenv`
  - `asyncio` (built-in)
  
- Google Gemini API key set in `.env`:
  ```env
  GEMINI_API_KEY=your_api_key_here

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/Indicium199/AI-Trail-Buddy-Pro.git
cd AI-Trail-Buddy-Pro

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API Keys
GEMINI_API_KEY=your_api_key_here

# Ensure trail data is present
trail_buddy/data/trails.csv

# Run AI Trail Buddy
python trail_buddy/main.py

## Use of AI Tools



