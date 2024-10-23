import geograpy
from rapidfuzz import process
from config.setup_nltk import setup_nltk_data
from utils.utils import load_country_codes, load_world_cities

# Ensure nltk data models are downloaded and setup in /data/nltk
setup_nltk_data()

# Load the country codes and world cities using your existing utils functions
country_codes_path = "data/country_codes.csv"
world_cities_path = "data/world_cities.csv"
country_code_dict = load_country_codes(country_codes_path)
city_country_dict = load_world_cities(world_cities_path)

# Example database of standardized place names for fuzzy matching
known_places = [
    "New York City", "Los Angeles", "San Francisco", "Austin, Texas", "London", 
    "Luxemburg", "Paris", "Tokyo", "Berlin", "Chicago", "Houston"
]

def normalize_place(location):
    """
    Normalize a location string by first extracting place names using geograpy,
    then using fuzzy matching to standardize the place name.

    Args:
        location (str): Input location string.

    Returns:
        tuple: (Matched place name, Score of the match).
    """
    if not location or location.lower() == "unknown":
        return "Unknown", 0

    try:
        # Use geograpy to extract places from the input
        places = geograpy.get_place_context(text=location)

        # If geograpy identifies a city, use fuzzy matching to standardize
        if places.cities:
            city = places.cities[0]
            match, score = process.extractOne(city, known_places)
            if score > 80:  # Only consider high-confidence fuzzy matches
                print(f"DEBUG: Fuzzy match for city '{city}': {match}, Score: {score}")
                return match, score

        # If geograpy identifies countries or regions, attempt matching
        if places.countries:
            country = places.countries[0]
            match, score = process.extractOne(country, known_places)
            if score > 80:  # Only consider high-confidence fuzzy matches
                print(f"DEBUG: Fuzzy match for country '{country}': {match}, Score: {score}")
                return match, score
        
        # If no cities or countries are found, apply fuzzy matching directly on the input location
        match, score = process.extractOne(location, known_places)
        print(f"DEBUG: Fuzzy match for location '{location}': {match}, Score: {score}")
        return (match, score) if score > 80 else ("Unknown", 0)
    except Exception as e:
        print(f"Error in normalizing place: {e}")
        return "Unknown", 0

# Test cases for debugging
if __name__ == "__main__":
    print(normalize_place("nyc"))              # Expected: New York City
    print(normalize_place("ny, ny"))           # Expected: New York City
    print(normalize_place("New York City"))    # Expected: New York City
    print(normalize_place("Austin, Texas"))    # Expected: Austin, Texas
    print(normalize_place("L.A."))             # Expected: Los Angeles
    print(normalize_place("Luxemburg"))        # Expected: Luxemburg
    print(normalize_place("Unknown"))          # Expected: Unknown, 0
