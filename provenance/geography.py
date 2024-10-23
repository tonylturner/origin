import json
from utils.utils import load_country_codes
from services.email_service import (
    resolve_domain_location,
    dns_mx_lookup,
    whois_lookup,
)
from provenance.normalize_place import normalize_place

# Load country codes
country_code_dict = load_country_codes("data/country_codes.csv")

# Load weights from weights.json
with open("provenance/weights.json", "r") as f:
    weights = json.load(f)

# Extract the correct weights from the JSON file
profile_weight = weights.get("profile_geo_weight", 0.4)
email_weight = weights.get("email_geo_weight", 0.3)
organization_weight = weights.get("organization_geo_weight", 0.3)

def debug_print(verbose, message):
    if verbose:
        print(message)


def normalize_country_name(country):
    """
    Normalize long-form country names to a short form (e.g., 'United States of America' to 'United States').
    Handles NoneType by returning 'Unknown'.
    """
    if country is None:
        return "Unknown"
    return country_code_dict.get(country.upper(), country)


def determine_final_location(
    email_geo, profile_geo, profile_geo_score, organization_geo="Unknown", verbose=False
):
    email_geo = email_geo or "Unknown"
    profile_geo = profile_geo or "Unknown"
    total_checks = 0
    confidence = 0
    profile_contribution = 0  # Initialize profile_contribution to avoid errors

    # Normalize and check Profile Geo
    normalized_profile_geo = normalize_country_name(profile_geo)
    if normalized_profile_geo != "Unknown":
        total_checks += 1
        profile_contribution = (profile_geo_score / 100) * profile_weight * 100
        confidence += profile_contribution  # Apply the weight from JSON for profile location

    debug_print(verbose, f"DEBUG: Normalized Profile Geo '{profile_geo}' to '{normalized_profile_geo}', contributing {profile_contribution:.2f}% to confidence")

    # Normalize and check Email Geo
    normalized_email_geo = normalize_country_name(email_geo)
    if normalized_email_geo != "Unknown" and profile_geo == "Unknown":
        total_checks += 1
        email_contribution = email_weight * 100  # Apply the weight from JSON for email location
        confidence += email_contribution
    else:
        email_contribution = 0

    debug_print(verbose, f"DEBUG: Normalized Email Geo '{email_geo}' to '{normalized_email_geo}' with confidence {email_contribution}")

    # Handle conflicts between profile and email geo
    if normalized_email_geo != "Unknown" and normalized_profile_geo != "Unknown":
        if normalized_email_geo != normalized_profile_geo:
            # Conflict detected, subtract email contribution from confidence
            debug_print(verbose, f"DEBUG: Conflict detected between email_geo '{normalized_email_geo}' and profile_geo '{normalized_profile_geo}'. Reducing confidence.")
            confidence -= email_contribution

    # Normalize and check Organization Geo
    if organization_geo != "Unknown":
        normalized_organization_geo = normalize_country_name(organization_geo)
        total_checks += 1
        confidence += organization_weight * 100  # Apply the weight from JSON for organization location
        debug_print(verbose, f"DEBUG: Normalized Organization Geo '{organization_geo}' to '{normalized_organization_geo}'")

    # Prioritize profile_geo if email_geo is unknown
    final_location = normalized_profile_geo if normalized_profile_geo != "Unknown" else normalized_email_geo

    # Cap confidence based on available data
    max_possible_confidence = (profile_weight * 100) + (email_weight * 100) + (organization_weight * 100)
    confidence = min(confidence, max_possible_confidence)

    debug_print(verbose, f"DEBUG: Total Checks: {total_checks}, Max Possible Confidence: {max_possible_confidence}, Final Confidence: {confidence:.2f}%")

    return final_location, confidence


def identify_geography(contributor, city_country_dict, verbose=False):
    """
    Identifies the geography of a contributor by analyzing their email, profile, and organization data.
    """
    # Accessing attributes from the NamedUser object
    username = getattr(contributor, "login", "Unknown")
    email = getattr(contributor, "email", "N/A")
    profile_geo = getattr(contributor, "location", "Unknown")
    organization = getattr(contributor, "company", "Unknown")

    email_geo = "Unknown"
    if email and "@" in email:
        domain_info = resolve_domain_location(email)
        email_geo = domain_info.get("country", "Unknown")

    # Normalize Profile Geo using normalize_place function
    normalized_place_data = normalize_place(profile_geo)  # Now returns a dict
    normalized_profile_geo = normalized_place_data.get("matched_place", "Unknown")
    profile_geo_score = normalized_place_data.get("score", 0)

    # Debug for normalize_place results
    debug_print(verbose, f"DEBUG: Profile Geo '{profile_geo}' matched with '{normalized_profile_geo}' (Score: {profile_geo_score})")

    final_location, confidence = determine_final_location(
        email_geo, normalized_profile_geo, profile_geo_score, organization, verbose=verbose
    )

    if email and "@" in email:
        domain = email.split("@")[-1]
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



# The second version of identify_geography is a fallback for contributors stored as dictionaries
def identify_geography_dict(contributor_dict, city_country_dict, verbose=False):
    """
    Fallback version of identify_geography that works on contributors stored as dictionaries
    instead of objects.
    """
    username = contributor_dict.get('login', 'Unknown')
    email = contributor_dict.get('email', 'N/A')
    profile_geo = contributor_dict.get('location', 'Unknown')
    organization = contributor_dict.get('company', 'Unknown')

    email_geo = "Unknown"
    if email and "@" in email:
        domain_info = resolve_domain_location(email)
        email_geo = domain_info.get("country", "Unknown")

    # Normalize Profile Geo using normalize_place function
    normalized_place_data = normalize_place(profile_geo)  # Now returns a dict
    normalized_profile_geo = normalized_place_data.get("matched_place", "Unknown")
    profile_geo_score = normalized_place_data.get("score", 0)

    # Debug for normalize_place results
    debug_print(verbose, f"DEBUG: Profile Geo '{profile_geo}' matched with '{normalized_profile_geo}' (Score: {profile_geo_score})")

    final_location, confidence = determine_final_location(
        email_geo, normalized_profile_geo, profile_geo_score, organization, verbose=verbose
    )

    if email and "@" in email:
        domain = email.split("@")[-1]
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
