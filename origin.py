import sys
import logging
import readline  # Enable tab completion for better CLI experience
from modules.linguistic_analysis import LinguisticAnalysis
from modules.devtools_analysis import DevToolsAnalysis
from config.argument_parser import parse_args, configure_logging
from config.setup_nltk import setup_nltk_data
from utils.cli import OriginCLI
from utils.menu import display_main_menu
from provenance.commit import analyze_commits

# Initialize engines
linguistic_analyzer = LinguisticAnalysis()
devtools_analyzer = DevToolsAnalysis()


def detect_contributor_origin(contributor_info, commit_messages):
    """
    Detect contributor's origin using metadata and linguistic analysis as fallback.

    Args:
        contributor_info (dict): Contributor metadata (e.g., email, organization).
        commit_messages (list): Commit messages for linguistic analysis.

    Returns:
        str: Likely origin of the contributor.
    """
    country_from_metadata = detect_origin_from_metadata(contributor_info)

    if country_from_metadata:
        return country_from_metadata

    # Fallback: Perform linguistic analysis on commit messages
    for message in commit_messages:
        logging.info(f"Analyzing commit message: {message}")

        # Perform linguistic analysis
        syntax_results = linguistic_analyzer.analyze_syntax(message)
        likely_origin = linguistic_analyzer.identify_origin_from_syntax(syntax_results)

        if likely_origin != "Unknown":
            return likely_origin

    return "Unknown"


def detect_origin_from_metadata(contributor_info):
    """
    Detect origin based on metadata like email domain or organization.

    Args:
        contributor_info (dict): Contributor metadata.

    Returns:
        str or None: Detected origin or None if no match.
    """
    email = contributor_info.get("email", "")
    organization = contributor_info.get("organization", "")

    if email.endswith(".cn"):
        return "China"
    elif organization.lower() == "russian dev group":
        return "Russia"
    return None


def perform_devtools_analysis(commit_metadata, logs, files):
    """
    Perform analysis on commit metadata, logs, and files.

    Args:
        commit_metadata (dict): Commit metadata for analysis.
        logs (str): Logs to analyze.
        files (list): List of files for localization or tool detection.
    """
    devtools_result = devtools_analyzer.analyze_commit_metadata(commit_metadata)
    compiler_language = devtools_analyzer.detect_compiler_language(logs)
    localization_settings = devtools_analyzer.detect_localization_settings(files)

    logging.info(f"DevTools Analysis Result: {devtools_result}")
    logging.info(f"Compiler Language: {compiler_language}")
    logging.info(f"Localization Settings: {localization_settings}")


def main():
    """
    Main entry point for the Origin tool.
    Handles command-line arguments and interactive menu options.
    """
    args = parse_args()
    configure_logging(args.verbose)
    setup_nltk_data(force_download=args.update_nltk)

    try:
        # Command-line mode
        if args.commit_analysis:
            logging.info("Running commit analysis...")
            owner, repo_name = args.repo_url.split("/")[-2:]
            analyze_commits(
                owner=owner,
                repo_name=repo_name,
                contributor=args.contributor,
                show_code=args.show_code,
                enable_commit_analysis=True,
            )
        elif args.adversarial:
            logging.info("Running adversarial analysis...")
            OriginCLI(args).provenance_menu(run_adversarial=True)
        elif args.repo_url:
            logging.info("Running provenance analysis and geography check...")
            OriginCLI(args).provenance_menu(run_geography_check=True)
        else:
            # Interactive menu mode
            while True:
                choice = display_main_menu()
                if choice == "1":
                    logging.info("Running Provenance Analysis...")
                    OriginCLI(args).provenance_menu()
                elif choice == "2":
                    logging.info("Running SBOM Analysis... (not yet implemented)")
                elif choice == "3":
                    logging.info("Running VCS Analysis... (not yet implemented)")
                elif choice == "4":
                    logging.info("Entering CLI Mode...")
                    OriginCLI(args).cmdloop()
                elif choice == "5":
                    logging.info("Exiting... Goodbye!")
                    break
                else:
                    logging.warning("Invalid choice. Please select a valid option.")
    except KeyboardInterrupt:
        logging.info("\nProcess interrupted. Exiting gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
