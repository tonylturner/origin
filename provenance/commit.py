from collections import defaultdict
import logging
from tqdm import tqdm
import github
from services.github_client import github_client
from modules.linguistic_analysis import LinguisticAnalysis
from colorama import Fore, Style

# Initialize linguistic analysis engine
linguistic_analyzer = LinguisticAnalysis()


# Fetch commits for a contributor with error handling and rate limit checking
def fetch_commits(repo, contributor, show_code=False):
    try:
        commits = list(repo.get_commits(author=contributor))
        return commits
    except github.RateLimitExceededException as e:
        logging.error(f"Rate limit exceeded for contributor {contributor.login}: {e}")
        headers = e.response.headers
        logging.error(f"Rate Limit Headers: {headers}")
        reset_time = headers.get("X-RateLimit-Reset")
        logging.error(f"Rate limit resets at: {reset_time}")
        return None
    except Exception as e:
        logging.error(f"Error fetching commits for {contributor.login}: {e}")
        return None


# Process commit details for a contributor with linguistic analysis
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

    with tqdm(
        total=commit_delta,
        desc=f"Analyzing commits for {contributor.login}",
        unit="commit",
        colour="red",
        leave=False,
    ) as commit_pbar:
        for commit in commits:
            commit_date = commit.commit.author.date.date()
            commit_dates[commit_date] += 1

            if commit.stats:
                total_insertions += commit.stats.additions
                total_deletions += commit.stats.deletions

            # Analyze commit message linguistically
            commit_message = commit.commit.message
            syntax_results = linguistic_analyzer.analyze_syntax(commit_message)
            ngrams = linguistic_analyzer.extract_ngrams(commit_message, n=2)
            code_patterns = linguistic_analyzer.extract_code_patterns(commit_message)
            likely_origin = linguistic_analyzer.identify_origin_from_syntax(
                syntax_results
            )

            # Add print statements to show linguistic analysis results
            print(
                f"\n{Fore.YELLOW}Linguistic Analysis for commit: {commit.sha}{Style.RESET_ALL}"
            )
            print(f"{Fore.GREEN}Commit Message:{Style.RESET_ALL} {commit_message}")
            print(
                f"{Fore.CYAN}Likely origin based on syntax:{Style.RESET_ALL} {likely_origin}"
            )
            print(f"{Fore.MAGENTA}Syntax Results:{Style.RESET_ALL} {syntax_results}")
            print(f"{Fore.BLUE}N-grams:{Style.RESET_ALL} {ngrams}")
            print(f"{Fore.LIGHTCYAN_EX}Code Patterns:{Style.RESET_ALL} {code_patterns}")
            print("-" * 50)  # Divider line for better clarity

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

    print(f"\n{Fore.YELLOW}Contributor: {contributor.login}{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}Commits:{Style.RESET_ALL} {commit_delta}")
    print(f"  {Fore.CYAN}First Commit Date:{Style.RESET_ALL} {first_commit}")
    print(f"  {Fore.CYAN}Last Commit Date:{Style.RESET_ALL} {last_commit}")
    print(
        f"  {Fore.CYAN}Commit Frequency:{Style.RESET_ALL} {commit_frequency} commits per day"
    )
    print(f"  {Fore.CYAN}Total Insertions:{Style.RESET_ALL} {total_insertions}")
    print(f"  {Fore.CYAN}Total Deletions:{Style.RESET_ALL} {total_deletions}")
    if burst_days:
        print(
            f"  {Fore.MAGENTA}Commit Bursts on:{Style.RESET_ALL} {', '.join(map(str, burst_days))}"
        )
    else:
        print(f"  {Fore.MAGENTA}No significant commit bursts detected{Style.RESET_ALL}")
    print(
        f"  {Fore.CYAN}Likely origin based on commit syntax:{Style.RESET_ALL} {likely_origin}"
    )

    return {
        "login": contributor.login,
        "commit_delta": commit_delta,
        "first_commit": first_commit,
        "last_commit": last_commit,
        "commit_frequency": commit_frequency,
        "total_insertions": total_insertions,
        "total_deletions": total_deletions,
        "commit_bursts": burst_days,
        "likely_origin": likely_origin,
    }


# New top-level function for commit analysis
def analyze_commits(
    owner, repo_name, contributor=None, show_code=False, enable_commit_analysis=True
):
    """
    Analyze commits for a repository. Optionally filter commits by a specific contributor.
    Only runs if `enable_commit_analysis` is True.

    Args:
        owner (str): Repository owner.
        repo_name (str): Repository name.
        contributor (str): Optional contributor to filter commits.
        show_code (bool): Whether to show detailed file changes in the commits.
        enable_commit_analysis (bool): Whether to run commit analysis.
    """
    print(
        f"\n{Fore.YELLOW}Analyzing commits for repository: {owner}/{repo_name}{Style.RESET_ALL}"
    )
    if not enable_commit_analysis:
        print("Commit analysis is disabled. Skipping...")
        return

    g = github_client()
    print(f"Analyzing commits for {owner}/{repo_name}...")

    repo = g.get_repo(f"{owner}/{repo_name}")

    if contributor:
        commits = fetch_commits(repo, contributor, show_code)
        if commits:
            process_commit_details(repo, contributor, commits, show_code)
        else:
            print(f"No commits found for contributor: {contributor}")
    else:
        contributors = repo.get_contributors()
        for contributor in contributors:
            commits = fetch_commits(repo, contributor, show_code)
            if commits:
                process_commit_details(repo, contributor, commits, show_code)
            else:
                print(f"No commits found for contributor: {contributor.login}")

    print(
        f"\n{Fore.GREEN}Finished analyzing commits for {owner}/{repo_name}.{Style.RESET_ALL}"
    )


def analyze_pull_requests(
    owner, repo_name, contributor=None, show_code=False, enable_pr_analysis=False
):
    """
    Analyze pull requests for a repository. Optionally filter by a specific contributor.
    Only runs if `enable_pr_analysis` is True.

    Args:
        owner (str): Repository owner.
        repo_name (str): Repository name.
        contributor (str): Optional contributor to filter pull requests.
        show_code (bool): Whether to show detailed file changes in the pull requests.
        enable_pr_analysis (bool): Whether to run pull request analysis.
    """
    if not enable_pr_analysis:
        print("Pull request analysis is disabled. Skipping...")
        return

    g = github_client()
    print(f"Analyzing pull requests for {owner}/{repo_name}...")

    repo = g.get_repo(f"{owner}/{repo_name}")

    pull_requests = repo.get_pulls(state="all")

    for pr in pull_requests:
        if contributor and pr.user.login != contributor:
            continue

        print(f"Analyzing PR #{pr.number}: {pr.title}")
        print(f"  Created by: {pr.user.login}")
        print(f"  Status: {pr.state}")
        print(f"  Merged: {pr.merged}")
        if show_code and pr.merged:
            pr_commits = pr.get_commits()
            for commit in pr_commits:
                print(f"    Commit: {commit.sha}")
                print(f"    Message: {commit.commit.message}")

    print(f"Finished analyzing pull requests for {owner}/{repo_name}.")


def parse_repo_url(repo_url):
    parts = repo_url.rstrip("/").split("/")
    owner, repo_name = parts[-2], parts[-1]
    return owner, repo_name
