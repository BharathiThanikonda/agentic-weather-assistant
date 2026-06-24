import asyncio
import os
import sys

import requests
from mcp.server import FastMCP
from dotenv import load_dotenv

if sys.platform == "win32":
    def _win_asyncio_exception_handler(loop, context):
        if isinstance(context.get("exception"), ConnectionResetError):
            return
        loop.default_exception_handler(context)

    _original_set_event_loop = asyncio.set_event_loop

    def _set_event_loop_with_handler(loop):
        if loop is not None:
            loop.set_exception_handler(_win_asyncio_exception_handler)
        _original_set_event_loop(loop)

    asyncio.set_event_loop = _set_event_loop_with_handler


load_dotenv()

OPENWEATHERMAP_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

app = FastMCP("Weather Agent", host="127.0.0.1", port=8080)

@app.tool()
def get_current_weather(city: str):
    """
    Use this tool to get the current weather for a specific city.
    It provides the temperature in Celsius and a brief description of the weather conditions.

    :param city: The name of the city to get the weather for (e.g., "London", "New York").
    """
    if not OPENWEATHERMAP_API_KEY:
        return "Error: The OpenWeatherMap API key is not configured. Please set the OPENWEATHERMAP_API_KEY environment variable."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"  # Use metric units
    }
    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 404:
            return f"Error: The city '{city}' was not found. Please check the spelling."
        
        response.raise_for_status()  # Raise an exception for other bad status codes (4xx or 5xx)
        data = response.json()

        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'Could not retrieve weather data.')}"

        main_weather = data.get("weather", [{}])[0]
        main_temp = data.get("main", {})

        temperature = main_temp.get("temp")
        conditions = main_weather.get("description")
        
        if temperature is not None and conditions:
            return f"The current temperature in {city} is {temperature}°C with {conditions}."
        else:
            return f"Could not retrieve full weather data for {city}."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while contacting the weather service: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@app.tool()
def get_forecast(city: str, days: int = 3):
    """
    Use this tool to get a daily weather forecast for a specific city for a number of days.
    It provides a summary of the average temperature and general conditions for each day.

    :param city: The city to get the forecast for (e.g., "Paris", "Tokyo").
    :param days: The number of days for the forecast, from 1 to 5. Defaults to 3.
    """
    if not OPENWEATHERMAP_API_KEY:
        return "Error: The OpenWeatherMap API key is not configured. Please set the OPENWEATHERMAP_API_KEY environment variable."

    if not 1 <= days <= 5:
        return "Error: Number of days for the forecast must be between 1 and 5."

    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 404:
            return f"Error: The city '{city}' was not found. Please check the spelling."

        response.raise_for_status()
        data = response.json()

        if str(data.get("cod")) != "200":
            return f"Error: {data.get('message', 'Could not retrieve forecast data.')}"

        forecast_items = data.get("list", [])
        daily_forecasts = {}

        for item in forecast_items:
            date = item["dt_txt"].split(" ")[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "temps": [],
                    "conditions": []
                }
            daily_forecasts[date]["temps"].append(item["main"]["temp"])
            daily_forecasts[date]["conditions"].append(item["weather"][0]["main"])

        if not daily_forecasts:
            return f"Could not generate a forecast for {city}."

        forecast_summary = f"Forecast for {city}:\n"
        day_count = 0
        for date, daily_data in daily_forecasts.items():
            if day_count >= days:
                break
            
            avg_temp = sum(daily_data["temps"]) / len(daily_data["temps"])
            # Get the most common condition for the day
            most_common_condition = max(set(daily_data["conditions"]), key=daily_data["conditions"].count)
            
            forecast_summary += f"- {date}: Avg Temp: {avg_temp:.1f}°C, Conditions: {most_common_condition}\n"
            day_count += 1

        return forecast_summary.strip()

    except requests.exceptions.RequestException as e:
        return f"An error occurred while contacting the weather service: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    print("Starting MCP server on http://127.0.0.1:8080/mcp ...")
    print("Make sure OPENWEATHERMAP_API_KEY is set in mcp-server/.env")
    app.run(transport="streamable-http")

