import os
from github import Github
from dotenv import load_dotenv

# Load the .env file and retrieve GitHub token
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def github_client():
    if not GITHUB_TOKEN:
        raise ValueError("GitHub token not found in .env file.")
    return Github(GITHUB_TOKEN)


def check_github_rate_limit():
    g = github_client()
    rate_limit = g.get_rate_limit()

    core_limit = rate_limit.core
    search_limit = rate_limit.search

    # Display core and search rate limits
    print("GitHub API Rate Limits:")
    print("  Core Rate Limit:")
    print(f"    Limit: {core_limit.limit}")
    print(f"    Remaining: {core_limit.remaining}")
    print(f"    Resets at: {core_limit.reset}")
    print("  Search Rate Limit:")
    print(f"    Limit: {search_limit.limit}")
    print(f"    Remaining: {search_limit.remaining}")
    print(f"    Resets at: {search_limit.reset}")

    # Additional checks for GraphQL and other rate limits
    if hasattr(rate_limit, 'graphql'):
        graphql_limit = rate_limit.graphql
        print("  GraphQL Rate Limit:")
        print(f"    Limit: {graphql_limit.limit}")
        print(f"    Remaining: {graphql_limit.remaining}")
        print(f"    Resets at: {graphql_limit.reset}")

    if hasattr(rate_limit, 'code_scanning_upload'):
        scanning_limit = rate_limit.code_scanning_upload
        print("  Code Scanning Upload Rate Limit:")
        print(f"    Limit: {scanning_limit.limit}")
        print(f"    Remaining: {scanning_limit.remaining}")
        print(f"    Resets at: {scanning_limit.reset}")
