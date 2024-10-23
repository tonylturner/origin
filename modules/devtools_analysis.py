import re


class DevToolsAnalysis:
    def __init__(self):
        pass

    def detect_compiler_language(self, logs):
        """
        Detects whether the compiler messages are in English or other languages.
        Looks for keywords in compiler messages such as "error" or "warning"
        and matches common non-English patterns.
        """
        if "error" in logs or "warning" in logs:
            if re.search(
                r"erreur|fehler|错误|ошибка", logs
            ):  # French, German, Chinese, Russian patterns
                return "Non-English compiler messages detected"
            return "English compiler messages detected"
        return "No compiler messages found"

    def detect_localization_settings(self, files):
        """
        Detects localization settings in configuration files or scripts, such as environment variables
        that specify locale (LANG, LC_ALL) or the use of gettext/locale in the project.
        """
        localization_settings = []
        for file in files:
            if re.search(r"LANG|LC_ALL|gettext|locale", file):
                localization_settings.append(file)
        return (
            localization_settings
            if localization_settings
            else "No localization settings detected"
        )

    def detect_timezone(self, commit_metadata):
        """
        Detects timezone and email domain information from commit metadata,
        useful for tracing the geographic origin of a developer.
        """
        timezone = commit_metadata.get("timezone")
        email = commit_metadata.get("email", "")
        email_domain = email.split("@")[-1] if email else "Unknown domain"
        if timezone:
            return f"Timezone: {timezone}, Email domain: {email_domain}"
        return "No useful timezone or domain metadata found"

    def detect_file_metadata(self, files_metadata):
        """
        Analyzes file metadata such as creation/modification times or document properties to trace origin.
        Useful for detecting file origins based on metadata.
        """
        file_metadata_results = []
        for metadata in files_metadata:
            if "creation_time" in metadata and "modification_time" in metadata:
                result = (
                    f"File created at {metadata['creation_time']}, "
                    f"last modified at {metadata['modification_time']}"
                )
                file_metadata_results.append(result)
        return (
            file_metadata_results if file_metadata_results else "No file metadata found"
        )

    def detect_locale_in_shell_scripts(self, script):
        """
        Searches shell scripts for localization environment variables (e.g., LANG, LC_ALL).
        """
        if re.search(r"export\s+(LANG|LC_ALL)\s*=", script):
            return "Localization settings found in shell script"
        return "No localization settings found in shell script"
