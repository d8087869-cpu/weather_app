import os
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

CSV_FILE = "weather_history.csv"

fieldnames = [
    "search_time",
    "city",
    "state",
    "country",
    "temperature",
    "feels_like",
    "condition",
    "humidity",
    "wind_speed"]


def get_location(city, country, state=""):
    if country == "US":
        location_query = f"{city},{state},{country}"
    else:
        location_query = f"{city},{country}"

    params = {
        "q": location_query,
        "limit": 1,
        "appid": API_KEY}
    try:
        response = requests.get(GEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("the request timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("Could not connect to the internet.")
        return None

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 401:
            print("Invalid API key.")
        else:
            print(f"HTTP error: {error.response.status_code}")
        return None

    if not data:
        return None

    return data[0]

def get_city():
    city = input("Enter city: ").strip()

    if city == "":
        print("city cannot be empty!")
        return None 
    
    return city

def get_country():
    country = input("Enter contry code: ").strip().upper()
    if len(country) != 2 or not country.isalpha():
        print("country must contain exactly tow letters.")
        return None
    return country

def get_state(country):
    if country == "US":
        state = input("Enter state code: ").strip().upper()

        if len(state) != 2 or not state.isalpha():
            print("State code must contain exactly two letters.")
            return None

        return state

    return None

def get_weather(latitude, longitude):
    params ={
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY,
        "units": "metric"}
    try:
        response = requests.get(WEATHER_URL, params= params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        print("The request timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("Could not connect to the internet.")
        return None

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 401:
            print("Invalid API key.")
        else:
            print(f"HTTP error: {error.response.status_code}")
        return None
    return data

def process_weather_data(location, weather):
    weather_result = {
        "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "city": location["name"],
        "state": location.get("state", ""),
        "country": location["country"],
        "temperature": weather["main"]["temp"],
        "feels_like": weather["main"]["feels_like"],
        "condition": weather["weather"][0]["description"],
        "humidity": weather["main"]["humidity"],
        "wind_speed": weather["wind"]["speed"]}
    
    return weather_result

def print_weather(weather_result):
    print(f"City: {weather_result['city']}")
    print(f"Country: {weather_result['country']}")

    if weather_result["state"]:
        print(f"State/Region: {weather_result['state']}")
        
    print(f"Temperature: {weather_result['temperature']}°C")
    print(f"Feels like: {weather_result['feels_like']}°C")
    print(f"Condition: {weather_result['condition']}")
    print(f"Humidity: {weather_result['humidity']}%")
    print(f"Wind speed: {weather_result['wind_speed']} m/s")

def save_weather_to_csv(weather_result):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()
            writer.writerow(weather_result)
    return True

def main():
    city = get_city()
    if city is None:
        return

    country = get_country()
    if country is None:
        return

    state = get_state(country)
    if country == "US" and state is None:
        return

    location = get_location(city, country, state)
    if location is None:
        print("Location not found.")
        return

    latitude = location["lat"]
    longitude = location["lon"]

    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")

    weather = get_weather(latitude, longitude)
    if weather is None:
        return

    weather_result = process_weather_data(location, weather)

    print_weather(weather_result)

    saved = save_weather_to_csv(weather_result)

    if saved:
        print("Weather result saved to weather_history.csv")


if __name__ == "__main__":
    main()
