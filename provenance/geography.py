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

def determine_final_location(
    email_geo, profile_geo, profile_geo_score, organization_geo="Unknown", verbose=False
):
    email_geo = email_geo or "Unknown"
    profile_geo = profile_geo or "Unknown"
    total_checks = 0
    confidence = 0

    # Normalize and check Email Geo
    normalized_email_geo = country_code_dict.get(email_geo.upper(), email_geo)
    if normalized_email_geo != "Unknown":
        total_checks += 1
        confidence += email_weight * 100  # Apply the weight from JSON for email location

    debug_print(verbose, f"DEBUG: Normalized Email Geo '{email_geo}' to '{normalized_email_geo}'")

    # Normalize and check Profile Geo
    if profile_geo != "Unknown":
        total_checks += 1
        # We factor in the profile_geo_score (from fuzzy matching)
        confidence += (profile_geo_score / 100) * profile_weight * 100  # Apply the weight from JSON for profile location
    else:
        profile_geo_score = 0

    debug_print(verbose, f"DEBUG: Normalized Profile Geo '{profile_geo}' with score {profile_geo_score}")

    # Normalize and check Organization Geo
    if organization_geo != "Unknown":
        normalized_organization_geo = country_code_dict.get(organization_geo.upper(), organization_geo)
        total_checks += 1
        confidence += organization_weight * 100  # Apply the weight from JSON for organization location

        debug_print(verbose, f"DEBUG: Normalized Organization Geo '{organization_geo}' to '{normalized_organization_geo}'")

    # Prioritize profile_geo if email_geo is unknown
    final_location = profile_geo if normalized_email_geo == "Unknown" else normalized_email_geo

    # If profile_geo is valid and email_geo is unknown, increase confidence
    if normalized_email_geo == "Unknown" and profile_geo != "Unknown":
        confidence = max(confidence, profile_geo_score)

    # Ensure confidence is capped at 100%
    confidence = min(confidence, 100)

    debug_print(verbose, f"DEBUG: Total Checks: {total_checks}, Final Confidence: {confidence:.2f}%")

    return final_location, confidence

def identify_geography(contributor, city_country_dict, verbose=False):
    """
    Identifies the geography of a contributor by analyzing their email, profile, and organization data.
    """
    username = contributor.login
    email = contributor.email or "N/A"
    profile_geo = contributor.location or "Unknown"
    organization = contributor.company or "Unknown"

    email_geo = "Unknown"
    if email and "@" in email:
        domain_info = resolve_domain_location(email)
        email_geo = domain_info.get("country", "Unknown")

    # Normalize Profile Geo using normalize_place function
    normalized_profile_geo, profile_geo_score = normalize_place(profile_geo)

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
