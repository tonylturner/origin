import csv


def load_country_codes(file_path):
    country_code_dict = {}
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            country_code_dict[row[1].upper()] = row[0]
    return country_code_dict


def load_world_cities(file_path):
    city_country_dict = {}
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        for line in csvfile:
            parts = line.strip().split(",")
            if len(parts) == 4:
                city, country, state, _ = parts
                city_country_dict[city.lower()] = (country, state)
    return city_country_dict
