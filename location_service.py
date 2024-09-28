import requests
from utils import load_world_cities

# Load city-country data
city_country_dict = load_world_cities("world_cities.csv")

def get_location_geolocation(city_name, city_country_dict):
    api_key = "your_locationiq_api_key"
    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={city_name}&format=json"

    try:
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            display_name = data[0].get("display_name", "")
            country_code = data[0].get("address", {}).get("country_code", "Unknown").upper()
            return country_code, display_name
        else:
            return "Unknown", "Unknown"
    except Exception as e:
        print(f"Error resolving city name {city_name}: {e}")
        return "Unknown", "Unknown"
