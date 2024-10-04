from collections import defaultdict
import logging
from tqdm import tqdm
import github

# Fetch commits for a contributor with error handling and rate limit checking
def fetch_commits(repo, contributor, show_code=False):
    try:
        commits = list(repo.get_commits(author=contributor))
        return commits
    except github.RateLimitExceededException as e:
        logging.error(f"Rate limit exceeded for contributor {contributor.login}: {e}")
        headers = e.response.headers
        logging.error(f"Rate Limit Headers: {headers}")
        reset_time = headers.get('X-RateLimit-Reset')
        logging.error(f"Rate limit resets at: {reset_time}")
        return None
    except Exception as e:
        logging.error(f"Error fetching commits for {contributor.login}: {e}")
        return None


# Process commit details for a contributor
def process_commit_details(repo, contributor, commits, show_code=False):
    commit_delta = len(commits)
    total_insertions = 0
    total_deletions = 0
    commit_dates = defaultdict(int)

    first_commit = commits[-1].commit.author.date if commit_delta > 0 else "N/A"
    last_commit = commits[0].commit.author.date if commit_delta > 0 else "N/A"
    
    if commit_delta > 1:
        time_range = (last_commit - first_commit).days
        commit_frequency = commit_delta / time_range if time_range > 0 else "N/A"
    else:
        commit_frequency = "N/A"

    with tqdm(total=commit_delta, desc=f"Analyzing commits for {contributor.login}", unit="commit", colour="red", leave=False) as commit_pbar:
        for commit in commits:
            commit_date = commit.commit.author.date.date()
            commit_dates[commit_date] += 1

            if commit.stats:
                total_insertions += commit.stats.additions
                total_deletions += commit.stats.deletions

            if show_code:
                commit_details = repo.get_commit(commit.sha)
                if commit_details.files:
                    logging.debug(f"Contributor: {contributor.login}")
                    logging.debug(f"Commit: {commit.sha}")
                    logging.debug("Files changed:")
                    for file in commit_details.files:
                        logging.debug(f"  - {file.filename}: {file.changes} changes")
                    logging.debug("\n")

            commit_pbar.update(1)

    burst_days = [date for date, count in commit_dates.items() if count > 3]

    print(f"Contributor: {contributor.login}")
    print(f"  Commits: {commit_delta}")
    print(f"  First Commit Date: {first_commit}")
    print(f"  Last Commit Date: {last_commit}")
    print(f"  Commit Frequency: {commit_frequency} commits per day")
    print(f"  Total Insertions: {total_insertions}")
    print(f"  Total Deletions: {total_deletions}")
    if burst_days:
        print(f"  Commit Bursts on: {', '.join(map(str, burst_days))}")
    else:
        print(f"  No significant commit bursts detected")

    return {
        "login": contributor.login,
        "commit_delta": commit_delta,
        "first_commit": first_commit,
        "last_commit": last_commit,
        "commit_frequency": commit_frequency,
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "commit_bursts": burst_days
    }
