import cmd
import readline
from provenance import adversarial_check, commit, contributor, geography
from utils.utils import load_country_codes
from services.github_client import github_client
from config.argument_parser import configure_logging  # Import configure_logging
import logging

enabled_modules = {
    "provenance_analysis": False,
    "sbom_analysis": False,
    "vcs_analysis": False,
}


class OriginCLI(cmd.Cmd):
    prompt = "> "

    intro = (
        "Welcome to the Origin CLI. Type 'help' or '?' to list available commands.\n"
    )

    def __init__(self, args=None):
        super().__init__()
        self.args = args or argparse.Namespace(
            verbose=False, repo_url=None, adversarial=False
        )
        configure_logging(self.args.verbose)  # Ensure logging is configured
        # Enable tab completion using readline
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")

    def do_modules(self, arg):
        """List available modules"""
        print("Available modules:")
        for module in enabled_modules:
            print(f"- {module}")

    def complete_modules(self, text, line, begidx, endidx):
        """Tab completion for the 'modules' command."""
        modules = ["provenance_analysis", "sbom_analysis", "vcs_analysis"]
        return [module for module in modules if module.startswith(text)]

    def do_use(self, arg):
        """Use a specific module"""
        if arg in enabled_modules:
            print(f"{arg} module loaded.")
            self.provenance_menu()
        else:
            print(f"No such module: {arg}")

    def complete_use(self, text, line, begidx, endidx):
        """Tab completion for the 'use' command."""
        return self.complete_modules(text, line, begidx, endidx)

    def provenance_menu(self, run_geography_check=False, run_adversarial=False):
        g = github_client()
        city_country_dict = load_country_codes("data/country_codes.csv")

        if self.args.repo_url:
            repo_url = self.args.repo_url
        else:
            repo_url = input("Enter the repository URL for provenance analysis: ")

        owner, repo_name = repo_url.split("/")[-2], repo_url.split("/")[-1]
        print(f"Running provenance analysis on {owner}/{repo_name}...")

        if run_adversarial:
            print("Running adversarial analysis...")
            contributors = contributor.get_contributors(
                g,
                owner,
                repo_name,
                show_commits=False,
                city_country_dict=city_country_dict,
            )
            adversarial_check.run_adversarial_analysis(
                owner, repo_name, contributors, city_country_dict
            )
            return

        if run_geography_check:
            print("Running provenance analysis and then geography check...")
            contributors = contributor.get_contributors(
                g,
                owner,
                repo_name,
                show_commits=False,
                city_country_dict=city_country_dict,
            )
            for contrib in contributors:
                geography.identify_geography(contrib, city_country_dict)
            return

        print("Provenance Analysis Menu:")
        print("1. Analyze commits")
        print("2. Analyze contributors")
        print("3. Perform geography check")
        print("4. Run adversarial analysis")
        print("5. Back to Main Menu")

        try:
            choice = input("Enter your choice: ")
            if choice == "1":
                print("Analyzing commits...")
                try:
                    commit.analyze_commits(owner, repo_name)
                except AttributeError:
                    print(
                        "Error: 'analyze_commits' function not found in commit module."
                    )
            elif choice == "2":
                print("Analyzing contributors...")
                contributors = contributor.get_contributors(
                    g,
                    owner,
                    repo_name,
                    show_commits=False,
                    city_country_dict=city_country_dict,
                )
            elif choice == "3":
                print("Running geography check...")
                contributors = contributor.get_contributors(
                    g,
                    owner,
                    repo_name,
                    show_commits=False,
                    city_country_dict=city_country_dict,
                )
                for contrib in contributors:
                    geography.identify_geography(contrib, city_country_dict)
            elif choice == "4":
                print("Running adversarial analysis...")
                contributors = contributor.get_contributors(
                    g,
                    owner,
                    repo_name,
                    show_commits=False,
                    city_country_dict=city_country_dict,
                )
                adversarial_check.run_adversarial_analysis(
                    owner, repo_name, contributors, city_country_dict
                )
            else:
                print("Returning to Main Menu")
        except KeyboardInterrupt:
            print("\nOperation canceled by user.")

    def do_enable(self, arg):
        """Enable a specific module"""
        if arg in enabled_modules:
            enabled_modules[arg] = True
            print(f"{arg} enabled")
        else:
            print(f"No such module: {arg}")

    def complete_enable(self, text, line, begidx, endidx):
        return self.complete_modules(text, line, begidx, endidx)

    def do_disable(self, arg):
        """Disable a specific module"""
        if arg in enabled_modules:
            enabled_modules[arg] = False
            print(f"{arg} disabled")
        else:
            print(f"No such module: {arg}")

    def complete_disable(self, text, line, begidx, endidx):
        return self.complete_modules(text, line, begidx, endidx)

    def do_show(self, arg):
        """Show enabled or disabled modules"""
        if arg == "enabled":
            print("Enabled modules:")
            for module, enabled in enabled_modules.items():
                if enabled:
                    print(f"- {module}")
        elif arg == "disabled":
            print("Disabled modules:")
            for module, enabled in enabled_modules.items():
                if not enabled:
                    print(f"- {module}")
        else:
            print('Specify "enabled" or "disabled"')

    def complete_show(self, text, line, begidx, endidx):
        return [option for option in ["enabled", "disabled"] if option.startswith(text)]

    def do_run(self, arg):
        """Run enabled modules"""
        if enabled_modules["provenance_analysis"]:
            repo_url = input("Enter the repository URL for provenance analysis: ")
            owner, repo_name = repo_url.split("/")[-2], repo_url.split("/")[-1]
            print(f"Running provenance analysis on {owner}/{repo_name}...")

            g = github_client()

            try:
                contributors = contributor.get_contributors(
                    g, owner, repo_name, show_commits=False
                )
                city_country_dict = load_country_codes("data/country_codes.csv")
                for contrib in contributors:
                    geography.identify_geography(contrib, city_country_dict)
                adversarial_check.run_adversarial_analysis(
                    owner, repo_name, contributors, city_country_dict
                )
            except AttributeError as e:
                print(f"Error: {e}")
        else:
            print("No modules enabled to run.")

    def do_exit(self, arg):
        """Exit the CLI"""
        print("Goodbye!")
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

    def do_question(self, arg):
        """Alias for help command"""
        return self.do_help(arg)

    def complete_help(self, text, line, begidx, endidx):
        """Tab completion for the 'help' command."""
        return [cmd for cmd in self.get_names() if cmd.startswith(f"do_{text}")]
