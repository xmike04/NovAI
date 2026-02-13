from NOVA.core.base_skill import BaseSkill
from NOVA.core.types import SkillResponse
import requests
from NOVA.config import config

class WeatherSkill(BaseSkill):
    def __init__(self):
        super().__init__()
        self.name = "WeatherSkill"
        self.intents = ["get_weather"]
        self.description = "Gets the current weather for a specific city or current location."
        self.slots = {"location": "City name (optional, defaults to current location)"}

    def execute(self, entities: dict) -> SkillResponse:
        city = entities.get("location", None)
        # Clean city name (remove punctuation like ?)
        if city:
             city = city.strip("?.!, ")
             
        response_text = self.fetch_weather(city)
        return SkillResponse(text=response_text)

    def get_ip_location(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            return data.get("city", "London")
        except:
            return "London"

    def fetch_weather(self, city=None):
        if not city or city.lower() in ["current", "current location", "here", "my location", "me"]:
            city = self.get_ip_location()
            
        api_key = config.weather_api_key
        units = "imperial"
        
        # Use Current Weather API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if data.get("cod") != 200:
                 return f"I couldn't find weather data for {city}."

            main = data["main"]
            weather = data["weather"][0]
            
            temp = round(main["temp"])
            desc = weather["description"]
            high = round(main["temp_max"])
            low = round(main["temp_min"])
            
            # Siri-like response
            response = (
                f"It's currently {temp} degrees and {desc} in {city}. "
                f"Expect a high of {high} degrees and a low of {low} degrees today."
            )
            return response

        except Exception as e:
            return f"Error fetching weather: {e}"