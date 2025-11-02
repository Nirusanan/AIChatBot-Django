from dotenv import load_dotenv
import os
import requests

# Load the environment variables from .env file
load_dotenv()

SERPER_API_KEY= os.environ.get("SERPER_API_KEY")
weather_api_key = os.environ.get("WEATHER_API_KEY")


def fetch_text_results(query: str) -> str:
    """Performs a Google search using Serper.dev and returns the top snippet."""
    try:
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "q": query
        }
        response = requests.post("https://google.serper.dev/search", json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract the top 3 snippets
        if "organic" in data and len(data["organic"]) > 0:
            results = []
            for result in data["organic"][:3]:  
                snippet = result.get("snippet", "No snippet found.")
                link = result.get("link", "")
                results.append(f"{snippet}\nLink: {link}")
    
            return "\n\n".join(results)
        else:
            return "No results found."

    except Exception as e:
        return f"Search failed: {str(e)}"


def get_weather(city: str)-> str:
    """Get weather for a given city."""

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        city_name = city
        temperature = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]

        return f"The weather in {city_name} is {temperature}°C with {humidity}% humidity and wind speed {wind_speed} m/s."
    else:
        return f"Could not get the weather for {city}. Please try again."


weather_function = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },

            },
            "required": ["location"],
        },
    }
}

internet_search = {
    "type": "function",
    "function": {
        "name": "fetch_text_results",
        "description": "Fetch text search results from Google Custom Search API",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string",
                },
                "start": {
                    "type": "integer",
                    "description": "The starting index of the results, for pagination",
                    "default": 1,
                },
            },
            "required": ["query"],
        },
    },
}
