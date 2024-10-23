from tqdm import tqdm
from provenance.geography import identify_geography

# List of adversarial or banned countries
BANNED_COUNTRIES = ["China", "Iran", "North Korea", "Cuba", "Venezuela", "Russia"]


# Function to run adversarial analysis on contributors
def run_adversarial_analysis(
    owner, repo_name, contributors, city_country_dict, verbose=False
):
    tqdm.write(f"Running adversarial analysis on {owner}/{repo_name}...")

    # Normalize banned countries for comparison
    banned_countries_normalized = [country.lower() for country in BANNED_COUNTRIES]

    # Analyze each contributor
    for contributor in tqdm(contributors, desc="Analyzing contributors"):
        geography = identify_geography(contributor, city_country_dict, verbose=verbose)
        final_location = geography["final_location"].strip().lower()

        # Check if the contributor's location is in the list of banned countries
        if final_location in banned_countries_normalized:
            # Only print contributor and final location without extra info
            tqdm.write(f"Contributor: {contributor.login}")
            tqdm.write(f"  Final Location: {geography['final_location']}")
