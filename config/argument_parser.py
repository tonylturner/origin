import argparse
import logging
import os

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
        # Do not make this required, so the program can fall back to the menu if not provided
    )

    # Analyze commits at the repository level
    parser.add_argument(
        "-c",
        "--commit-analysis",
        action="store_true",
        help="Enable commit analysis at the repository level.",
    )

    # Analyze commits for a specific contributor
    parser.add_argument(
        "-u",
        "--contributor",
        type=str,
        help="Specify a contributor to analyze commits for.",
    )

    # Analyze pull requests at the repository level
    parser.add_argument(
        "-r",
        "--pr-analysis",
        action="store_true",
        help="Enable pull request analysis at the repository level.",
    )

    # Show commit details and code changes for each commit
    parser.add_argument(
        "-x",
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
        "-a",
        "--adversarial",
        action="store_true",
        help="Only return contributors from adversarial countries",
    )

    # Purge application log file before starting
    parser.add_argument(
        "--purge-logs", 
        action="store_true", 
        help="Purge the application log file before starting."
    )

    # Force NLTK data update
    parser.add_argument(
        "--update-nltk",
        action="store_true",
        help="Force updating NLTK data models",
    )

    return parser.parse_args()


def configure_logging(verbosity, purge_logs=False):
    log_file = "logs/app.log"

    # Purge log file if requested
    if purge_logs and os.path.exists(log_file):
        with open(log_file, 'w'):
            pass
        print(f"Log file {log_file} purged.")

    # Configure logging based on the verbosity level
    if verbosity == 1:
        logging.basicConfig(level=logging.ERROR, format="%(message)s", filename=log_file)
    elif verbosity == 2:
        logging.basicConfig(level=logging.WARNING, format="%(message)s", filename=log_file)
    elif verbosity >= 3:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s", filename=log_file)
    else:
        logging.basicConfig(level=logging.CRITICAL, format="%(message)s", filename=log_file)

    # Adjust logging for third-party libraries like 'whois' if necessary
    whois_logger = logging.getLogger("whois")
    if verbosity >= 3:
        whois_logger.setLevel(logging.DEBUG)
    else:
        whois_logger.setLevel(logging.CRITICAL)  # Suppress whois logging unless in debug mode
