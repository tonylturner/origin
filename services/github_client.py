
import os
from github import Github
from dotenv import load_dotenv
import logging

# Load the .env file and retrieve GitHub token
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def github_client():
    if not GITHUB_TOKEN:
        logger.error("GitHub token not found in .env file.")
        raise ValueError("GitHub token not found in .env file.")
    return Github(GITHUB_TOKEN)


def check_github_rate_limit():
    g = github_client()
    rate_limit = g.get_rate_limit()

    core_limit = rate_limit.core
    search_limit = rate_limit.search

    # Display core and search rate limits
    logger.info("GitHub API Rate Limits:")
    logger.info("  Core Rate Limit:")
    logger.info(f"    Limit: {core_limit.limit}")
    logger.info(f"    Remaining: {core_limit.remaining}")
    logger.info(f"    Resets at: {core_limit.reset}")
    logger.info("  Search Rate Limit:")
    logger.info(f"    Limit: {search_limit.limit}")
    logger.info(f"    Remaining: {search_limit.remaining}")
    logger.info(f"    Resets at: {search_limit.reset}")

    # Additional checks for GraphQL and other rate limits
    if hasattr(rate_limit, 'graphql'):
        graphql_limit = rate_limit.graphql
        logger.info("  GraphQL Rate Limit:")
        logger.info(f"    Limit: {graphql_limit.limit}")
        logger.info(f"    Remaining: {graphql_limit.remaining}")
        logger.info(f"    Resets at: {graphql_limit.reset}")

    if hasattr(rate_limit, 'code_scanning_upload'):
        scanning_limit = rate_limit.code_scanning_upload
        logger.info("  Code Scanning Upload Rate Limit:")
        logger.info(f"    Limit: {scanning_limit.limit}")
        logger.info(f"    Remaining: {scanning_limit.remaining}")
        logger.info(f"    Resets at: {scanning_limit.reset}")
