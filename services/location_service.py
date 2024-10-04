import requests
import logging
from utils.utils import load_world_cities

# Initialize logger
logger = logging.getLogger(__name__)

# Load city-country data
city_country_dict = load_world_cities("data/world_cities.csv")


def get_location_geolocation(city_name, city_country_dict):
    api_key = os.getenv("LOCATIONIQ_API_KEY")
    if not api_key:
        logger.error("LocationIQ API key not found in environment variables.")
        raise ValueError("LocationIQ API key not found in environment variables.")

    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={city_name}&format=json"

    try:
        logger.debug(f"Making request to LocationIQ API for city: {city_name}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            display_name = data[0].get("display_name", "")
            country_code = (
                data[0].get("address", {}).get("country_code", "Unknown").upper()
            )
            logger.debug(f"LocationIQ API response: {display_name}, {country_code}")
            return country_code, display_name
        else:
            logger.warning(f"No results found for city name {city_name}.")
            return "Unknown", "Unknown"
    except requests.RequestException as e:
        logger.error(f"Error resolving city name {city_name} via LocationIQ API: {e}")
        return "Unknown", "Unknown"
