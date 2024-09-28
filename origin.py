from tqdm import tqdm
import os
import logging
from github_client import github_client, check_github_rate_limit
from location_service import get_location_geolocation
from email_service import dns_mx_lookup, whois_lookup, resolve_domain_location
from utils import load_country_codes, load_world_cities
from geography import identify_geography
from dotenv import load_dotenv
from urllib.parse import urlparse
from argument_parser import parse_args
import logging_config  # Import the logging config module

# Load the .env file and retrieve GitHub token and API keys
load_dotenv()

# Define the path for country codes and cities
COUNTRY_CODES_CSV = "country_codes.csv"
WORLD_CITIES_CSV = "world_cities.csv"

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
        tqdm.write(f"  Final Location: {geography['final_location']} with {geography['confidence']:.2f}% confidence\n")

# Get contributors from a repository with a progress bar
def get_contributors(g, owner, repo_name, show_commits=False, show_code=False, verbose=False, adversarial=False):
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except Exception as e:
        logging.error(f"Error accessing repository {owner}/{repo_name}: {e}")
        return []

    # Get total count of contributors
    contributors = repo.get_contributors()
    total_contributors = contributors.totalCount

    # Use tqdm for a progress bar
    with tqdm(total=total_contributors, desc="Analyzing contributors", unit="contributor", colour="green", leave=True) as pbar:
        if adversarial:
            for contributor in contributors:
                adversarial_check(contributor, city_country_dict, verbose=verbose)
                pbar.update(1)  # Update the progress bar
        else:
            contributor_list = []
            for contributor in contributors:
                commit_delta = (
                    repo.get_commits(author=contributor).totalCount if show_commits else "N/A"
                )

                if show_code:
                    commits = repo.get_commits(author=contributor)
                    for commit in commits:
                        commit_details = repo.get_commit(commit.sha)
                        if commit_details.files:
                            logging.debug("  Files changed:")
                            for file in commit_details.files:
                                logging.debug(f"    - {file.filename}: {file.changes} changes")
                        logging.debug("\n")

                # Get geography without printing anything
                geography = identify_geography(contributor, city_country_dict, verbose=verbose)

                # Only print contributor details if not in adversarial mode
                tqdm.write(f"Contributor Profile Location (raw from GitHub): {contributor.location or 'Unknown'}")
                tqdm.write(f"Contributor: {contributor.login}")
                tqdm.write(f"  Email: {contributor.email or 'N/A'}")
                tqdm.write(f"  Email-based Location: {geography['email_geo']}")
                tqdm.write(f"  Profile Location: {geography['profile_geo']}")
                tqdm.write(f"  Organization: {contributor.company or 'Not provided'}")
                tqdm.write(f"  Final Location: {geography['final_location']} with {geography['confidence']:.2f}% confidence\n")

                user_data = {
                    "login": contributor.login,
                    "contributions": contributor.contributions,
                    "html_url": contributor.html_url,
                    "email": contributor.email or "N/A",
                    "commit_delta": commit_delta,
                    "geography": geography,
                }
                contributor_list.append(user_data)

                pbar.update(1)  # Update the progress bar

            return contributor_list

# Main execution
if __name__ == "__main__":
    try:
        args = parse_args()
        logging_config.setup_logging(args)  # Setup logging using logging_config

        # Check API rate limits if requested
        if args.rate_limit:
            check_github_rate_limit()
            exit()

        # Initialize GitHub client
        g = github_client()

        # Extract owner and repo name from URL
        owner, repo_name = parse_github_url(args.repo_url)

        # Get the list of contributors for the base repository
        contributors = get_contributors(
            g, owner, repo_name, show_commits=args.commits, show_code=args.show_code, verbose=args.verbose, adversarial=args.adversarial
        )

        # Output to CSV if requested and not in adversarial mode
        if args.csv and not args.adversarial:
            write_to_csv(contributors)
            print(f"Contributors data exported to contributors.csv")

    except KeyboardInterrupt:
        tqdm.write("\nProcess interrupted by user. Exiting gracefully.")
