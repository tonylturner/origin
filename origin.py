import sys
import os
import logging
import readline  # Import readline to enable tab completion

from modules.linguistic_analysis import LinguisticAnalysis
from config.argument_parser import parse_args, configure_logging
from config.setup_nltk import setup_nltk_data  # Ensure NLTK models are handled
from utils.cli import OriginCLI  # Import the CLI class from utils.cli
from utils.menu import display_main_menu  # Import the menu display function
from provenance.commit import analyze_commits

# Initialize linguistic analysis engine
linguistic_analyzer = LinguisticAnalysis()


# Function to detect contributor origin using metadata and linguistic analysis as a fallback
def detect_contributor_origin(contributor_info, commit_messages):
    # Use metadata (GitHub profile, email, etc.) for origin detection first
    country_from_metadata = detect_origin_from_metadata(contributor_info)

    if country_from_metadata:
        return country_from_metadata

    # Fallback: Perform linguistic analysis on commit messages
    for message in commit_messages:
        print(f"Analyzing commit message: {message}")

        # Perform linguistic analysis
        syntax_results = linguistic_analyzer.analyze_syntax(message)
        code_patterns = linguistic_analyzer.extract_code_patterns(message)

        # Infer origin from linguistic patterns
        likely_origin = linguistic_analyzer.identify_origin_from_syntax(syntax_results)
        if likely_origin != "Unknown":
            return likely_origin

    return "Unknown"


# Function to detect origin based on metadata (e.g., email domain or organization)
def detect_origin_from_metadata(contributor_info):
    # Simple checks based on email domain or organization
    if contributor_info.get("email") and contributor_info["email"].endswith(".cn"):
        return "China"
    elif contributor_info.get("organization") == "Russian Dev Group":
        return "Russia"
    return None


# Main function to handle the workflow based on command-line arguments or menu interaction
def main():
    args = parse_args()
    configure_logging(args.verbose)
    setup_nltk_data(force_download=args.update_nltk)

    try:
        # Command-line arguments
        if args.commit_analysis:
            print("Running commit analysis...")
            owner, repo_name = (
                args.repo_url.split("/")[-2],
                args.repo_url.split("/")[-1],
            )
            analyze_commits(
                owner,
                repo_name,
                contributor=args.contributor,
                show_code=args.show_code,
                enable_commit_analysis=True,
            )
        elif args.adversarial:
            print("Running adversarial analysis...")
            OriginCLI(args).provenance_menu(run_adversarial=True)
        elif args.repo_url:
            print("Running provenance analysis and geography check...")
            OriginCLI(args).provenance_menu(run_geography_check=True)
        else:
            # No arguments provided, fall back to the main menu
            while True:
                choice = display_main_menu()
                if choice == "1":
                    print("Running Provenance Analysis...")
                    OriginCLI(args).provenance_menu()
                elif choice == "2":
                    print("Running SBOM Analysis... (not yet implemented)")
                elif choice == "3":
                    print("Running VCS Analysis... (not yet implemented)")
                elif choice == "4":
                    print("Entering CLI Mode...")
                    OriginCLI(args).cmdloop()
                elif choice == "5":
                    print("Exiting... Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
