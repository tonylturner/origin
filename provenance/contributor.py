import time
import random
import logging
from collections import defaultdict
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from provenance.geography import identify_geography
from provenance.commit import fetch_commits
from github.GithubException import GithubException, RateLimitExceededException

# Exponential backoff with jitter
def exponential_backoff(attempt, max_delay=120):
    delay = min(2 ** attempt + random.uniform(0, 1), max_delay)
    logging.warning(f"Backing off for {delay:.2f} seconds before retrying...")
    time.sleep(delay)

# Fetch commits with exponential backoff
def fetch_commits_with_backoff(repo, contributor, show_code, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            return fetch_commits(repo, contributor, show_code)
        except RateLimitExceededException as e:
            logging.warning(f"Rate limit exceeded for contributor {contributor.login}: {e}")
            exponential_backoff(attempt)
            attempt += 1
        except GithubException as e:
            logging.error(f"GitHub error for contributor {contributor.login}: {e}")
            exponential_backoff(attempt)  # Backoff on general GitHub errors
            attempt += 1
        except Exception as e:
            logging.error(f"Unexpected error for contributor {contributor.login}: {e}")
            break
    return None

# Get contributors and their commits from a repository with dual progress bars
def get_contributors(
    g,
    owner,
    repo_name,
    show_commits=False,
    show_code=False,
    verbose=False,
    adversarial=False,
    city_country_dict=None,  # Pass in the city-country dictionary
):
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
    except Exception as e:
        logging.error(f"Error accessing repository {owner}/{repo_name}: {e}")
        return []

    # Get total count of contributors
    contributors = repo.get_contributors()
    total_contributors = contributors.totalCount

    # If showing commit deltas or code details, process commits
    if show_commits or show_code:
        contributor_list = []

        # Limit the number of concurrent workers to reduce API pressure
        with ThreadPoolExecutor(max_workers=2) as executor:  # Lower concurrency to avoid rate limits
            futures = {
                executor.submit(fetch_commits_with_backoff, repo, contributor, show_code): contributor
                for contributor in contributors
            }

            with tqdm(total=total_contributors, desc="Analyzing contributors", unit="contributor", colour="green") as contributor_pbar:
                for future in as_completed(futures):
                    contributor = futures[future]
                    result = future.result()

                    if result is None:
                        logging.error(f"Failed to fetch commits for {contributor.login}")
                        continue

                    # Print commit delta and additional commit-related information
                    print(f"Contributor: {result['login']}")
                    print(f"  Commits: {result['commit_delta']}")
                    print(f"  First Commit Date: {result['first_commit']}")
                    print(f"  Last Commit Date: {result['last_commit']}")
                    print(f"  Commit Frequency: {result['commit_frequency']} commits per day")
                    print(f"  Total Insertions: {result['total_insertions']}")
                    print(f"  Total Deletions: {result['total_deletions']}")
                    if result["commit_bursts"]:
                        print(f"  Commit Bursts on: {', '.join(map(str, result['commit_bursts']))}")
                    else:
                        print(f"  No significant commit bursts detected")

                    contributor_list.append(result)
                    contributor_pbar.update(1)

        return contributor_list

    # If geography lookup is required, use tqdm for progress bar
    with tqdm(
        total=total_contributors,
        desc="Analyzing contributors",
        unit="contributor",
        colour="green",
        leave=True,
    ) as pbar:
        if adversarial:
            for contributor in contributors:
                adversarial_check(contributor, city_country_dict, verbose=verbose)
                pbar.update(1)  # Update the progress bar
        else:
            contributor_list = []
            for contributor in contributors:
                # Perform geography lookups
                geography = identify_geography(contributor, city_country_dict, verbose=verbose)

                # Print geography details
                tqdm.write(f"Contributor Profile Location (raw from GitHub): {contributor.location or 'Unknown'}")
                tqdm.write(f"Contributor: {contributor.login}")
                tqdm.write(f"  Email-based Location: {geography['email_geo']}")
                tqdm.write(f"  Profile Location: {geography['profile_geo']}")
                tqdm.write(f"  Final Location: {geography['final_location']} with {geography['confidence']:.2f}% confidence\n")

                user_data = {
                    "login": contributor.login,
                    "geography": geography,
                }
                contributor_list.append(user_data)
                pbar.update(1)  # Update the progress bar

            return contributor_list
