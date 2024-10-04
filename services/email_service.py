import dns.resolver
import whois
import time
import signal
import logging
from config import logging_config  # Correct path to logging_config

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

# Initialize logger using logging_config
logger = logging.getLogger(__name__)


def dns_mx_lookup(email_domain):
    try:
        mx_records = dns.resolver.resolve(email_domain, "MX")
        return [str(r.exchange) for r in mx_records]
    except dns.resolver.NoAnswer as e:
        # Log to app.log (always) and console (only on -vvv)
        logger.error(f"DNS MX lookup failed for {email_domain}: {e}")
        return []
    except Exception as e:
        # Log to app.log (always) and console (only on -vvv)
        logger.error(f"DNS MX lookup failed for {email_domain}: {e}")
        return []


# Timeout handler for signal
def timeout_handler(signum, frame):
    raise TimeoutError


# WHOIS lookup function with timeout and retry mechanism
def whois_lookup(domain, retries=3, timeout=10):
    # Set the signal handler for the timeout
    signal.signal(signal.SIGALRM, timeout_handler)

    for attempt in range(retries):
        try:
            # Start the alarm for the timeout duration
            signal.alarm(timeout)
            logger.debug(f"Attempting WHOIS lookup for {domain}, attempt {attempt + 1}")

            # Perform the whois lookup
            response = whois.whois(domain)

            # Cancel the alarm if successful
            signal.alarm(0)

            # Check if the response is valid and not empty
            if response is None:
                raise Exception("WHOIS response is None")

            # Extract country and org from response
            country = response.get("country", "Unknown") if response else "Unknown"
            org = response.get("org", "Unknown") if response else "Unknown"

            return country, org
        except TimeoutError:
            logger.warning(
                f"WHOIS lookup timed out for {domain}, attempt {attempt + 1}"
            )
        except Exception as e:
            # Log to app.log (always) and console (only on -vvv)
            logger.error(
                f"WHOIS lookup failed for {domain} at attempt {attempt + 1}: {e}"
            )

        # Wait before retrying
        time.sleep(2)

    # Remove the alarm in case of failure after retries
    signal.alarm(0)

    # Return Unknown if all retries fail
    return "Unknown", "Unknown"


def resolve_domain_location(email):
    domain = email.split("@")[-1] if "@" in email else email
    if domain in FREE_EMAIL_DOMAINS:
        return {
            "domain": domain,
            "mx_records": [],
            "country": "Unknown",  # Always default to "Unknown" if it's a free email domain
            "organization": "Unknown",
        }

    # Default values for country and organization
    country = "Unknown"
    org = "Unknown"

    try:
        logger.debug(f"Resolving DNS MX records for {domain}")
        mx_records = dns_mx_lookup(domain)

        logger.debug(f"Attempting WHOIS lookup for {domain}")
        country, org = whois_lookup(domain)
    except Exception as e:
        # Log error if WHOIS or DNS fails, but only in debug
        logger.error(f"Error during DNS/WHOIS lookup for {domain}: {e}")
        mx_records = []

    # Return the results, ensuring country is never None
    return {
        "domain": domain,
        "mx_records": mx_records,
        "country": country
        or "Unknown",  # Ensuring "Unknown" as a default if the country is None
        "organization": org or "Unknown",  # Same for organization
    }
