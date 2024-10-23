import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cmd
import argparse
import logging

from config.argument_parser import parse_args, configure_logging
from config.setup_nltk import setup_nltk_data  # Ensure NLTK models are handled
from provenance import adversarial_check, commit, contributor, geography
from utils.utils import load_country_codes
from services.github_client import github_client  # Use github_client to initialize GitHub

enabled_modules = {
    'provenance_analysis': False,
    'sbom_analysis': False,
    'vcs_analysis': False
}

def display_main_menu():
    print("\nMain Menu:")
    print("1. Run Provenance Analysis")
    print("2. Run SBOM Analysis")
    print("3. Run VCS Analysis")
    print("4. CLI Mode (Advanced)")
    print("5. Exit")
    choice = input("Enter your choice (1-5): ")
    return choice

class OriginCLI(cmd.Cmd):
    prompt = '> '
    
    intro = "Welcome to the Origin CLI. Type 'help' to list available commands.\n"

    def __init__(self, args=None):
        super().__init__()
        self.args = args or argparse.Namespace(verbose=False)  # Provide default args with verbose=False
        configure_logging(self.args.verbose)

    def do_modules(self, arg):
        """List available modules"""
        print('Available modules:')
        for module in enabled_modules:
            print(f'- {module}')

    def do_use(self, arg):
        """Use a specific module"""
        if arg == 'provenance_analysis':
            print(f'{arg} module loaded.')
            self.provenance_menu()
        else:
            print(f'No such module: {arg}')

    def provenance_menu(self):
        # Initialize GitHub object using the github_client function
        g = github_client()
        
        # Load the city-country dictionary
        city_country_dict = load_country_codes("data/country_codes.csv")
        
        # Prompt the user for a repository URL before running provenance analysis
        repo_url = input("Enter the repository URL for provenance analysis: ")
        owner, repo_name = repo_url.split('/')[-2], repo_url.split('/')[-1]
        print(f"Running provenance analysis on {owner}/{repo_name}...")
        
        print('Provenance Analysis Menu:')
        print('1. Analyze commits')
        print('2. Analyze contributors')
        print('3. Perform geography check')
        print('4. Run adversarial analysis')
        print('5. Back to Main Menu')
        try:
            choice = input('Enter your choice: ')
            if choice == '1':
                print('Analyzing commits...')
                try:
                    commit.analyze_commits(owner, repo_name)  # Updated function to use owner and repo_name
                except AttributeError:
                    print("Error: 'analyze_commits' function not found in commit module.")
            elif choice == '2':
                print('Analyzing contributors...')
                contributors = contributor.get_contributors(g, owner, repo_name, show_commits=False, city_country_dict=city_country_dict)
            elif choice == '3':
                print('Running geography check...')
                # Perform geography check for contributors
                contributors = contributor.get_contributors(g, owner, repo_name, show_commits=False, city_country_dict=city_country_dict)
                for contrib in contributors:
                    geography.identify_geography(contrib, city_country_dict)
            elif choice == '4':
                print('Running adversarial analysis...')
                adversarial_check.run_adversarial_analysis(owner, repo_name)  # Updated function with owner and repo_name
            else:
                print('Returning to Main Menu')
        except KeyboardInterrupt:
            print("\nOperation canceled by user.")

    def do_enable(self, arg):
        """Enable a specific module"""
        if arg in enabled_modules:
            enabled_modules[arg] = True
            print(f'{arg} enabled')
        else:
            print(f'No such module: {arg}')

    def do_disable(self, arg):
        """Disable a specific module"""
        if arg in enabled_modules:
            enabled_modules[arg] = False
            print(f'{arg} disabled')
        else:
            print(f'No such module: {arg}')

    def do_show(self, arg):
        """Show enabled or disabled modules"""
        if arg == 'enabled':
            print('Enabled modules:')
            for module, enabled in enabled_modules.items():
                if enabled:
                    print(f'- {module}')
        elif arg == 'disabled':
            print('Disabled modules:')
            for module, enabled in enabled_modules.items():
                if not enabled:
                    print(f'- {module}')
        else:
            print('Specify "enabled" or "disabled"')

    def do_run(self, arg):
        """Run enabled modules"""
        if enabled_modules['provenance_analysis']:
            repo_url = input("Enter the repository URL for provenance analysis: ")
            owner, repo_name = repo_url.split('/')[-2], repo_url.split('/')[-1]
            print(f"Running provenance analysis on {owner}/{repo_name}...")
            try:
                commit.analyze_commits(owner, repo_name)  # Placeholder function call
            except AttributeError:
                print("Error: 'analyze_commits' function not found in commit module.")
            contributors = contributor.get_contributors(g, owner, repo_name, show_commits=False)  # Placeholder function call
            city_country_dict = load_country_codes("data/country_codes.csv")
            for contrib in contributors:
                geography.identify_geography(contrib, city_country_dict)  # Provide city_country_dict
            adversarial_check.run_adversarial_analysis(owner, repo_name)  # Placeholder function call
        else:
            print('No modules enabled to run.')

    def do_exit(self, arg):
        """Exit the CLI"""
        print('Goodbye!')
        return True

    def do_help(self, arg):
        """Display help for commands"""
        print("Available commands:")
        print("  modules - List available modules")
        print("  use <module> - Use a specific module")
        print("  enable <module> - Enable a specific module")
        print("  disable <module> - Disable a specific module")
        print("  show <enabled|disabled> - Show enabled or disabled modules")
        print("  run - Run enabled modules")
        print("  exit - Exit the CLI")

def main():
    # Parse arguments, including --update-nltk
    args = parse_args()

    # Configure logging verbosity
    configure_logging(args.verbose)

    # Set up NLTK models, force downloading if --update-nltk is provided
    setup_nltk_data(force_download=args.update_nltk)

    # If a repo URL is provided, directly run provenance analysis
    if args.repo_url:
        print("Running provenance analysis...")
        OriginCLI(args).provenance_menu()
    elif len(sys.argv) == 1:
        # No arguments provided, start the interactive menu
        try:
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
    else:
        print("Usage: python3 origin.py")

if __name__ == '__main__':
    main()
