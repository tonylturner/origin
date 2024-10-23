import sys
import os
import argparse
import logging
import readline  # Import readline to enable tab completion

from modules.linguistic_analysis import LinguisticAnalysis

from config.argument_parser import parse_args, configure_logging
from config.setup_nltk import setup_nltk_data  # Ensure NLTK models are handled
from utils.cli import OriginCLI  # Import the CLI class from utils.cli
from utils.menu import display_main_menu  # Import the menu display function

linguistic_analyzer = LinguisticAnalysis()

def detect_contributor_origin(contributor_info, commit_messages):
    # Existing logic: Check GitHub profile, organization, email for origin detection
    country_from_metadata = detect_origin_from_metadata(contributor_info)
    
    if country_from_metadata:
        return country_from_metadata
    
    # Fallback: Perform linguistic analysis on commit messages
    for message in commit_messages:
        print(f"Analyzing commit message: {message}")
        
        # Get linguistic features
        syntax_results = linguistic_analyzer.analyze_syntax(message)
        code_patterns = linguistic_analyzer.extract_code_patterns(message)
        
        # Attempt to infer origin from linguistic patterns
        likely_origin = linguistic_analyzer.identify_origin_from_syntax(syntax_results)
        if likely_origin != "Unknown":
            return likely_origin
    
    return "Unknown"

def detect_origin_from_metadata(contributor_info):
    # Example logic to detect origin based on email or organization
    if contributor_info.get('email') and contributor_info['email'].endswith('.cn'):
        return "China"
    elif contributor_info.get('organization') == "Russian Dev Group":
        return "Russia"
    return None


def main():
    args = parse_args()
    configure_logging(args.verbose)
    setup_nltk_data(force_download=args.update_nltk)

    try:
        if args.adversarial:
            print("Running adversarial analysis...")
            OriginCLI(args).provenance_menu(run_adversarial=True)
        elif args.repo_url:
            print("Running provenance analysis and geography check...")
            OriginCLI(args).provenance_menu(run_geography_check=True)
        else:
            while True:
                choice = display_main_menu()
                if choice == '1':
                    print("Running Provenance Analysis...")
                    OriginCLI(args).provenance_menu()
                elif choice == '2':
                    print("Running SBOM Analysis... (not yet implemented)")
                elif choice == '3':
                    print("Running VCS Analysis... (not yet implemented)")
                elif choice == '4':
                    print("Entering CLI Mode...")
                    OriginCLI(args).cmdloop()
                elif choice == '5':
                    print("Exiting... Goodbye!")
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
    except KeyboardInterrupt:
        print("\nProcess interrupted. Exiting gracefully.")
        sys.exit(0)

if __name__ == '__main__':
    main()
