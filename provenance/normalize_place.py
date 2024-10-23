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
    "Luxemburg", "Paris", "Tokyo", "Berlin", "Chicago", "Houston", "United States of America"
]

def normalize_place(location):
    """
    Normalize a location string by first extracting place names using geograpy,
    then using fuzzy matching or country_codes.csv as a fallback.

    Args:
        location (str): Input location string.

    Returns:
        dict: A dictionary containing matched place name, score, and other extracted details.
    """
    if not location or location.lower() == "unknown":
        print(f"DEBUG: Location '{location}' is unknown or empty. Returning default.")
        return {"matched_place": "Unknown", "score": 0, "geograpy_data": {}, "fuzzy_match": {}}

    try:
        # Use geograpy to extract places from the input
        places = geograpy.get_place_context(text=location)

        # Log all geograpy results for clarity
        geograpy_data = {
            "countries": places.countries,
            "regions": places.regions,
            "cities": places.cities,
            "other": places.other
        }
        print(f"DEBUG: Geograpy data extracted from '{location}': {geograpy_data}")

        # Initialize return data structure
        result = {"geograpy_data": geograpy_data, "fuzzy_match": {}, "matched_place": "Unknown", "score": 0}

        # If Geograpy finds a country, return it as a match
        if places.countries:
            country = places.countries[0]
            print(f"DEBUG: Country '{country}' identified by geograpy. Using as the matched place.")
            result["matched_place"] = country
            result["score"] = 100
            return result

        # If Geograpy identifies a city, use fuzzy matching to standardize
        if places.cities:
            city = places.cities[0]
            match, score, _ = process.extractOne(city, known_places)
            print(f"DEBUG: Fuzzy match for city '{city}': {match}, Score: {score}")
            result["fuzzy_match"] = {"type": "city", "match": match, "score": score}
            if score > 80:
                result["matched_place"] = match
                result["score"] = score
                return result

        # Fallback: Check country_codes.csv if Geograpy fails to identify
        country_from_csv = country_code_dict.get(location.upper(), None)
        if country_from_csv:
            country_name = country_from_csv.split(",")[0]  # Extract the full country name
            print(f"DEBUG: Fallback to country_codes.csv for location '{location}': Matched country '{country_name}'.")
            result["matched_place"] = country_name
            result["score"] = 100
            return result

        # If all else fails, apply fuzzy matching directly on the input location
        match, score, _ = process.extractOne(location, known_places)
        print(f"DEBUG: Fuzzy match for location '{location}': {match}, Score: {score}")
        result["fuzzy_match"] = {"type": "direct", "match": match, "score": score}
        if score > 80:
            result["matched_place"] = match
            result["score"] = score

        return result
    except Exception as e:
        print(f"Error in normalizing place: {e}")
        return {"matched_place": "Unknown", "score": 0, "geograpy_data": {}, "fuzzy_match": {}}

# Test cases for debugging
if __name__ == "__main__":
    print(normalize_place("nyc"))              # Expected: New York City
    print(normalize_place("ny, ny"))           # Expected: New York City
    print(normalize_place("New York City"))    # Expected: New York City
    print(normalize_place("Austin, Texas"))    # Expected: Austin, Texas
    print(normalize_place("L.A."))             # Expected: Los Angeles
    print(normalize_place("Luxemburg"))        # Expected: Luxemburg
    print(normalize_place("Unknown"))          # Expected: Unknown, 0
    print(normalize_place("Anahola, HI"))      # Expected: Handle city and state
    print(normalize_place("United States"))    # Expected: United States of America
    print(normalize_place("NL"))               # Expected: Netherlands from fallback
