import argparse
import logging

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch contributors, forks, and commit details from a GitHub repository using a URL."
    )

    # GitHub repository URL
    parser.add_argument(
        "-p",
        "--repo-url",
        type=str,
        help="GitHub repository URL (e.g., https://github.com/octocat/Hello-World)",
    )

    # Show commit deltas for each contributor
    parser.add_argument(
        "-c",
        "--commits",
        action="store_true",
        help="Show commit deltas for each contributor",
    )

    # Show commit details and code changes for each contributor
    parser.add_argument(
        "--show-code",
        action="store_true",
        help="Show the commit details and code changes for each contributor",
    )

    # Export results to a CSV file
    parser.add_argument(
        "--csv", action="store_true", help="Export the results to a CSV file"
    )

    # Check GitHub and LocationIQ API rate limits
    parser.add_argument(
        "--rate-limit",
        action="store_true",
        help="Check API rate limits for GitHub and LocationIQ",
    )

    # Enable verbose output for logging
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for errors, -vv for warnings, -vvv for debug)",
    )

    # Only return contributors from adversarial countries
    parser.add_argument(
        "--adversarial",
        action="store_true",
        help="Only return contributors from adversarial countries",
    )

    # Force NLTK data update
    parser.add_argument(
        "--update-nltk",
        action="store_true",
        help="Force updating NLTK data models",
    )

    return parser.parse_args()



def configure_logging(verbosity):
    # Configure logging based on the verbosity level
    if verbosity == 1:
        logging.basicConfig(level=logging.ERROR, format="%(message)s")
    elif verbosity == 2:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")
    elif verbosity >= 3:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.CRITICAL, format="%(message)s")

    # Adjust logging for third-party libraries like 'whois' if necessary
    whois_logger = logging.getLogger("whois")
    if verbosity >= 3:
        whois_logger.setLevel(logging.DEBUG)
    else:
        whois_logger.setLevel(
            logging.CRITICAL
        )  # Suppress whois logging unless in debug mode
