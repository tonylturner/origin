import sys
import os
import argparse
import logging
import readline  # Import readline to enable tab completion

from config.argument_parser import parse_args, configure_logging
from config.setup_nltk import setup_nltk_data  # Ensure NLTK models are handled
from utils.cli import OriginCLI  # Import the CLI class from utils.cli
from utils.menu import display_main_menu  # Import the menu display function

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
