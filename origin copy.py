import os
import argparse
from github_client import github_client, check_github_rate_limit
from location_service import get_location_geolocation
from email_service import dns_mx_lookup, whois_lookup
from utils import load_country_codes, load_world_cities
from dotenv import load_dotenv
from urllib.parse import urlparse
from geography import fuzzy_city_country_match

# Load the .env file and retrieve GitHub token and API keys
load_dotenv()

# Define the path for country codes
COUNTRY_CODES_CSV = "country_codes.csv"
WORLD_CITIES_CSV = "world_cities.csv"

# Load country codes and city-country mappings
country_code_dict = load_country_codes(COUNTRY_CODES_CSV)
city_country_dict = load_world_cities(WORLD_CITIES_CSV)

# List of common free email domains to ignore
FREE_EMAIL_DOMAINS = [
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "aol.com",
    "icloud.com",
    "mail.com",
    "protonmail.com",
]

# Debug print function that respects the verbose flag
def debug_print(verbose, message):
    if verbose:
        print(message)

def determine_final_location(email_geo, profile_geo, organization_geo="Unknown", verbose=False):
    # Initialize votes and the total checks count
    votes = 0
    total_checks = 0

    # Normalize and check Email Geo
    normalized_email_geo = country_code_dict.get(email_geo.upper(), email_geo)  # Normalize to long form
    if normalized_email_geo != "Unknown":
        votes += 1
    total_checks += 1
    debug_print(verbose, f"DEBUG: Normalized Email Geo '{email_geo}' to '{normalized_email_geo}'")

    # Normalize and check Profile Geo
    normalized_profile_geo = country_code_dict.get(profile_geo.upper(), profile_geo)  # Normalize to long form
    if normalized_profile_geo != "Unknown":
        votes += 1
    total_checks += 1
    debug_print(verbose, f"DEBUG: Normalized Profile Geo '{profile_geo}' to '{normalized_profile_geo}'")

    # Normalize and check Organization Geo
    if organization_geo != "Unknown":
        normalized_organization_geo = country_code_dict.get(organization_geo.upper(), organization_geo)  # Normalize to long form
        total_checks += 1  # Count the organization check, but do not add to votes
        debug_print(verbose, f"DEBUG: Normalized Organization Geo '{organization_geo}' to '{normalized_organization_geo}'")

    # Calculate confidence
    confidence = (votes / total_checks) * 100 if total_checks > 0 else 0

    # Debug output for vote counts
    debug_print(verbose, f"DEBUG: Votes: {votes}, Total Checks: {total_checks}, Confidence: {confidence:.2f}%")

    # Final location based on the first valid location found
    final_location = normalized_email_geo if normalized_email_geo != "Unknown" else normalized_profile_geo

    return final_location, min(confidence, 100)

def resolve_domain_location(email):
    domain = email.split("@")[-1] if "@" in email else email
    if domain in FREE_EMAIL_DOMAINS:
        return {
            "domain": domain,
            "mx_records": [],
            "country": "Unknown",
            "organization": "Unknown",
        }

    mx_records = dns_mx_lookup(domain)
    country, org = whois_lookup(domain)

    return {
        "domain": domain,
        "mx_records": mx_records,
        "country": country,
        "organization": org,
    }

def identify_geography(contributor, verbose=False):
    username = contributor.login
    email = contributor.email or "N/A"
    profile_geo = contributor.location or "Unknown"  # Raw profile location from GitHub
    organization = contributor.company or "Unknown"

    email_geo = "Unknown"
    if email and "@" in email:
        domain_info = resolve_domain_location(email)
        email_geo = domain_info["country"]

    # Normalize profile location using the location API
    if profile_geo != "Unknown":
        country_code, normalized_profile_geo = get_location_geolocation(profile_geo, city_country_dict)
    else:
        normalized_profile_geo = profile_geo

    # Debug print for raw profile location from GitHub
    print(f"Contributor Profile Location (raw from GitHub): {profile_geo}")

    # Debug prints for verbose mode
    debug_print(verbose, f"DEBUG: Email Geo: {email_geo}, Profile Geo: {normalized_profile_geo}")

    # Use normalized values for determining the final location
    final_location, confidence = determine_final_location(email_geo, normalized_profile_geo, organization, verbose=verbose)

    if email and "@" in email:
        domain = email.split('@')[-1]
        debug_print(verbose, f"DNS and WHOIS for domain: {domain}")
        debug_print(verbose, f"  MX Records: {', '.join(dns_mx_lookup(domain))}")
        debug_print(verbose, f"  WHOIS Country: {email_geo}")

    print(f"Contributor: {username}")
    print(f"  Email: {email}")
    print(f"  Email-based Location: {email_geo}")
    print(f"  Profile Location: {profile_geo}")  # Always print the raw GitHub profile location
    print(f"  Organization: {organization if organization != 'Unknown' else 'Not provided'}")
    print(f"  Final Location: {final_location} with {confidence:.2f}% confidence\n")

    return {
        "username": username,
        "email": email,
        "email_geo": email_geo,
        "profile_geo": profile_geo,  # Raw profile location from GitHub
        "organization_geo": organization,  # Include organization for consistency
        "final_location": final_location,
        "confidence": confidence,
    }

# Extract owner and repository name from URL
def parse_github_url(repo_url):
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) != 2:
        raise ValueError(f"Invalid GitHub URL: {repo_url}")

    owner, repo_name = path_parts
    return owner, repo_name

# Get contributors from a repository
def get_contributors(g, owner, repo_name, show_commits=False, show_code=False, verbose=False):
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except Exception as e:
        print(f"Error accessing repository {owner}/{repo_name}: {e}")
        return []

    contributors = repo.get_contributors()
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
                    print("  Files changed:")
                    for file in commit_details.files:
                        print(f"    - {file.filename}: {file.changes} changes")
                print("\n")

        geography = identify_geography(contributor, verbose=verbose)

        user_data = {
            "login": contributor.login,
            "contributions": contributor.contributions,
            "html_url": contributor.html_url,
            "email": contributor.email or "N/A",
            "commit_delta": commit_delta,
            "geography": geography,
        }
        contributor_list.append(user_data)

    return contributor_list

# Main function to handle arguments and initiate analysis
def parse_args():
    parser = argparse.ArgumentParser(description='Fetch contributors, forks, and commit details from a GitHub repository using a URL.')
    parser.add_argument('-p', '--repo-url', type=str, required=True, help='GitHub repository URL (e.g., https://github.com/octocat/Hello-World)')
    parser.add_argument('-c', '--commits', action='store_true', help='Show commit deltas for each contributor')
    parser.add_argument('--show-code', action='store_true', help='Show the commit details and code changes for each contributor')
    parser.add_argument('--csv', action='store_true', help='Export the results to a CSV file')
    parser.add_argument('--rate-limit', action='store_true', help='Check API rate limits for GitHub and LocationIQ')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output (print debug statements)')
    return parser.parse_args()

# Main execution
if __name__ == "__main__":
    try:
        args = parse_args()

        # Check API rate limits if requested
        if args.rate_limit:
            check_github_rate_limit()
            check_locationiq_rate_limit()
            exit()

        # Initialize GitHub client
        g = github_client()

        # Extract owner and repo name from URL
        owner, repo_name = parse_github_url(args.repo_url)

        # Get the list of contributors for the base repository
        contributors = get_contributors(g, owner, repo_name, show_commits=args.commits, show_code=args.show_code, verbose=args.verbose)

        if args.csv:
            write_to_csv(contributors)
            print(f"Contributors data exported to contributors.csv")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting gracefully.")
