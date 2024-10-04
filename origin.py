from tqdm import tqdm
import os
import logging
from services.github_client import github_client, check_github_rate_limit
from services.location_service import get_location_geolocation
from services.email_service import dns_mx_lookup, whois_lookup, resolve_domain_location
from utils.utils import load_country_codes, load_world_cities
from provenance.geography import identify_geography
from provenance.contributor import get_contributors
from dotenv import load_dotenv
from urllib.parse import urlparse
from config.argument_parser import parse_args
import config.logging_config as logging_config  # Import the logging config module
import sys

# Load the .env file and retrieve GitHub token and API keys
load_dotenv()

# Define the path for country codes and cities
COUNTRY_CODES_CSV = os.path.join("data", "country_codes.csv")
WORLD_CITIES_CSV = os.path.join("data", "world_cities.csv")

# Load country codes and city-country mappings
country_code_dict = load_country_codes(COUNTRY_CODES_CSV)
city_country_dict = load_world_cities(WORLD_CITIES_CSV)

BANNED_COUNTRIES = ["China", "Iran", "North Korea", "Cuba", "Venezuela", "Russia"]


# Extract owner and repository name from URL
def parse_github_url(repo_url):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) != 2:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    owner, repo_name = path_parts
    return owner, repo_name


# Check if the contributor is from an adversarial country
def adversarial_check(contributor, city_country_dict, verbose=False):
    geography = identify_geography(contributor, city_country_dict, verbose=verbose)

    # Normalize final location to match against banned countries
    final_location = geography["final_location"].strip().lower()
    banned_countries_normalized = [country.lower() for country in BANNED_COUNTRIES]

    # Only print contributors from banned countries
    if final_location in banned_countries_normalized:
        tqdm.write(f"Contributor: {contributor.login}")
        tqdm.write(
            f"  Final Location: {geography['final_location']} with {geography['confidence']:.2f}% confidence\n"
        )


# Main execution
if __name__ == "__main__":
    try:
        args = parse_args()
        logging_config.setup_logging(args)  # Setup logging using logging_config

        # Check API rate limits if requested
        if args.rate_limit:
            check_github_rate_limit()
            sys.exit(0)  # Exit after displaying rate limits

        # Initialize GitHub client
        g = github_client()

        # Extract owner and repo name from URL
        owner, repo_name = parse_github_url(args.repo_url)

        # Get the list of contributors for the base repository
        contributors = get_contributors(
            g,
            owner,
            repo_name,
            show_commits=args.commits,
            show_code=args.show_code,
            verbose=args.verbose,
            adversarial=args.adversarial,
            city_country_dict=city_country_dict  # Pass the necessary data
        )

        # Output to CSV if requested and not in adversarial mode
        if args.csv and not args.adversarial:
            write_to_csv(contributors)
            print(f"Contributors data exported to contributors.csv")

    except KeyboardInterrupt:
        tqdm.write("\nProcess interrupted by user. Exiting gracefully.")
