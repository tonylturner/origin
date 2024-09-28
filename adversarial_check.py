# Check if the contributor is from an adversarial country
def adversarial_check(contributor, city_country_dict, verbose=False):
    geography = identify_geography(contributor, city_country_dict, verbose=verbose)

    # Normalize final location to match against banned countries
    final_location = geography["final_location"].strip().lower()
    banned_countries_normalized = [country.lower() for country in BANNED_COUNTRIES]

    # Only print contributors from banned countries
    if final_location in banned_countries_normalized:
        print(f"Contributor: {contributor.login}")
        print(f"  Final Location: {geography['final_location']} with {geography['confidence']:.2f}% confidence\n")
