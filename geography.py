from difflib import get_close_matches
from utils import load_country_codes
from email_service import resolve_domain_location, dns_mx_lookup, whois_lookup  # Correct imports
from location_service import get_location_geolocation

country_code_dict = load_country_codes("country_codes.csv")

def debug_print(verbose, message):
    if verbose:
        print(message)

def determine_final_location(email_geo, profile_geo, organization_geo="Unknown", verbose=False):
    # Ensure email_geo is not None
    email_geo = email_geo or "Unknown"

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


def fuzzy_city_country_match(city_name, city_country_dict):
    city_name = city_name.lower().strip()

    # Check for a direct match including state
    if city_name in city_country_dict:
        country, state = city_country_dict[city_name]
        return country, state

    # Fuzzy match using Levenshtein distance if no direct match is found
    close_matches = get_close_matches(city_name, city_country_dict.keys(), n=1, cutoff=0.8)
    if close_matches:
        matched_city = close_matches[0]
        country, state = city_country_dict[matched_city]
        return country, state

    # Attempt to split city, state, and country if applicable (e.g., "City, State, Country")
    parts = [part.strip() for part in city_name.split(",")]

    if len(parts) == 2:  # "City, State" format
        city, state = parts
        if city in city_country_dict:
            country, _ = city_country_dict[city]
            return country, state
    elif len(parts) >= 3:  # "City, State, Country" format
        city = parts[0]
        state = parts[1]
        country = parts[-1]  # Use the last part as the country
        if country in country_code_dict:
            return country_code_dict[country], state

    # If all else fails, return unknown
    return "Unknown", "Unknown"

def identify_geography(contributor, city_country_dict, verbose=False):
    username = contributor.login
    email = contributor.email or "N/A"
    profile_geo = contributor.location or "Unknown"
    organization = contributor.company or "Unknown"

    email_geo = "Unknown"
    if email and "@" in email:
        domain_info = resolve_domain_location(email)
        email_geo = domain_info["country"]

    normalized_profile_geo = "Unknown"

    # Handle profile_geo and attempt to split and match
    if profile_geo != "Unknown":
        parts = [part.strip() for part in profile_geo.split(",")]

        if len(parts) == 2:  # Likely "city, state" format
            city, state = parts
            if city in city_country_dict:
                country_code, _ = city_country_dict[city]
                normalized_profile_geo = country_code
            else:
                # If city not found, attempt fuzzy matching
                country_code, normalized_profile_geo = fuzzy_city_country_match(profile_geo, city_country_dict)
        elif len(parts) >= 3:  # Likely "city, state, country"
            city = parts[0]
            state = parts[1]
            country = parts[-1]
            if country in country_code_dict:
                normalized_profile_geo = country_code_dict[country]
            else:
                # Fuzzy match to fallback
                country_code, normalized_profile_geo = fuzzy_city_country_match(profile_geo, city_country_dict)
        else:
            # If it's a single value, treat as a city and fuzzy match
            country_code, normalized_profile_geo = fuzzy_city_country_match(profile_geo, city_country_dict)

    debug_print(verbose, f"DEBUG: Contributor Profile Location (raw from GitHub): {profile_geo}")
    debug_print(verbose, f"DEBUG: Email Geo: {email_geo}, Profile Geo: {normalized_profile_geo}")

    # Use normalized values for determining the final location
    final_location, confidence = determine_final_location(email_geo, normalized_profile_geo, organization, verbose=verbose)

    if email and "@" in email:
        domain = email.split('@')[-1]
        debug_print(verbose, f"DNS and WHOIS for domain: {domain}")
        debug_print(verbose, f"  MX Records: {', '.join(dns_mx_lookup(domain))}")
        debug_print(verbose, f"  WHOIS Country: {email_geo}")

    return {
        "username": username,
        "email": email,
        "email_geo": email_geo,
        "profile_geo": profile_geo,
        "organization_geo": organization,
        "final_location": final_location,
        "confidence": confidence,
    }
