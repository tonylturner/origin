import csv
import logging

# Initialize logger
logger = logging.getLogger(__name__)


def load_country_codes(file_path):
    """
    Load country codes from a CSV file. The CSV should have two columns:
    Country Name and Country Code.

    Args:
        file_path (str): Path to the country codes CSV file.

    Returns:
        dict: A dictionary where the key is the country code (uppercased)
              and the value is the country name.
    """
    country_code_dict = {}
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                country_code_dict[row[1].upper()] = row[0]
        logger.debug(f"Successfully loaded country codes from {file_path}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}, Error: {e}")
    except Exception as e:
        logger.error(f"Error loading country codes from {file_path}: {e}")

    return country_code_dict


def load_world_cities(file_path):
    """
    Load world cities from a CSV file. The CSV should have four columns:
    City, Country, State, and Population.

    Args:
        file_path (str): Path to the world cities CSV file.

    Returns:
        dict: A dictionary where the key is the city name (lowercased)
              and the value is a tuple of (country, state).
    """
    city_country_dict = {}
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            for line in csvfile:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    city, country, state, _ = parts
                    city_country_dict[city.lower()] = (country, state)
        logger.debug(f"Successfully loaded world cities from {file_path}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}, Error: {e}")
    except Exception as e:
        logger.error(f"Error loading world cities from {file_path}: {e}")

    return city_country_dict
