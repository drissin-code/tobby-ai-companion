import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY = "palakkad"


def get_weather(city=None):
    if city is None:
        city = DEFAULT_CITY

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200:
            return f"Couldn't get weather for {city}: {data.get('message', 'unknown error')}"

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        return (
            f"It's currently {temp:.0f}°C in {city}, feels like {feels_like:.0f}°C, "
            f"with {description}. Humidity is at {humidity}%."
        )

    except requests.exceptions.RequestException:
        return "Sorry, I couldn't reach the weather service right now."


if __name__ == "__main__":
    print(get_weather())
