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
    print("GitHub API Rate Limit:")
    print(f"  Limit: {core_limit.limit}")
    print(f"  Remaining: {core_limit.remaining}")
    print(f"  Reset Time: {core_limit.reset}")
