# modules/config.py
from modules.config_utils import test_database_connection, test_github_access, verify_email_settings, verify_fio_api_key
import os
import json
import subprocess

class Config:
    DEFAULT_STRUCTURE = {
        "database": {
            "host": "",
            "port": "",
            "name": "",
            "user": "",
            "password": ""
        },
        "github": {
            "create_issues": False,
            "repo_name": "",
            "pat": ""
        },
        "email": {
            "enable_notifications": False,
            "smtp_server": "",
            "smtp_port": 587,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": ""
        }
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.settings = {}

        # Attempt to load existing configuration
        try:
            self.load()
        except Exception as e:
            print(f"Failed to load configuration: {e}. Starting setup...")

        # Run setup to ensure all required fields are properly set
        self.setup()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as file:
                    self.settings = json.load(file)
                    if not self.is_valid():
                        print("Configuration file is invalid or incomplete. Starting setup...")
                        self.setup()
                    else:
                        self.test_config()
            except json.JSONDecodeError:
                print(f"Error: Could not parse {self.config_file}. Starting setup...")
                self.setup()
        else:
            print(f"Configuration file {self.config_file} not found. Starting setup...")
            self.setup()

    def is_valid(self):
        # Validate that all required sections and keys exist
        for section, keys in self.DEFAULT_STRUCTURE.items():
            if section not in self.settings or not isinstance(self.settings[section], dict):
                return False
            for key in keys:
                if key not in self.settings[section]:
                    return False
        return True

    def setup(self):

        # Ensure all sections exist
        self.settings.setdefault("database", {})
        self.settings.setdefault("fio", {})
        self.settings.setdefault("github", {})
        self.settings.setdefault("email", {})

        if (not self.settings["database"] or not test_database_connection(**self.settings["database"])
                or not self.settings["fio"] or not self.settings["fio"].get("api_key")
                or not self.settings["github"] or not test_github_access(self.settings["github"].get("repo_name", ""),
                                                                         self.settings["github"].get("pat", ""))
                or self.settings["email"]["enable_notifications"] is None):
            print("Let's set up your configuration.")


            # Database settings (Ensure all are set and valid)
            if not self.settings["database"] or not test_database_connection(**self.settings["database"]):
                print("\nDatabase Settings:")
                while True:
                    self.settings["database"]["host"] = input(
                        f"Database Host [{self.settings['database'].get('host', 'localhost')}]: ") or self.settings[
                                                            "database"].get("host", "localhost")
                    self.settings["database"]["port"] = input(
                        f"Database Port [{self.settings['database'].get('port', '3306')}]: ") or self.settings[
                                                            "database"].get("port", "3306")
                    self.settings["database"]["name"] = input(
                        f"Database Name [{self.settings['database'].get('name', '')}]: ") or self.settings["database"].get(
                        "name", "")
                    self.settings["database"]["user"] = input(
                        f"Database User [{self.settings['database'].get('user', '')}]: ") or self.settings["database"].get(
                        "user", "")
                    self.settings["database"]["password"] = input("Database Password [hidden]: ")
                    if test_database_connection(**self.settings["database"]):
                        print("Database connection successful!")
                        break
                    print("Database connection failed. Please try again.")

            # FIO settings (Ensure API key is present and valid)
            if not self.settings["fio"] or not self.settings["fio"].get("api_key"):
                print("\nFIO Settings:")
                while True:
                    self.settings["fio"]["api_key"] = input(
                        f"FIO API Key [{self.settings['fio'].get('api_key', '')}]: ") or self.settings["fio"].get(
                        "api_key", "")
                    if self.settings["fio"]["api_key"] and verify_fio_api_key(self.settings["fio"]["api_key"]):
                        print("FIO API Key is valid and set successfully!")
                        break
                    print("Invalid FIO API Key. Please enter a valid key.")

            # GitHub settings (Ensure all required fields are set)
            if not self.settings["github"] or not test_github_access(self.settings["github"].get("repo_name", ""),
                                                                     self.settings["github"].get("pat", "")):
                print("\nGitHub Settings:")
                self.settings["github"]["create_issues"] = input(
                    f"Automatically report bugs and exceptions? (yes/no) [{self.settings['github'].get('create_issues', False)}]: ").lower() == "yes"
                if self.settings["github"]["create_issues"]:
                    default_repo = self.get_default_repo()
                    while True:
                        self.settings["github"]["repo_name"] = input(
                            f"GitHub Repo Name [{self.settings['github'].get('repo_name', default_repo)}]: ") or \
                                                               self.settings["github"].get("repo_name", default_repo)
                        self.settings["github"]["pat"] = input("GitHub Personal Access Token (PAT): ")
                        if test_github_access(self.settings["github"]["repo_name"], self.settings["github"]["pat"]):
                            print("GitHub access successful!")
                            break
                        print("GitHub access failed. Please try again.")

            # Email notifications settings (Ensure optional fields are properly configured)
            if self.settings["email"]["enable_notifications"] is None:
                print("\nEmail Notifications Settings:")
                if not self.settings["email"].get("enable_notifications", False):
                    self.settings["email"]["enable_notifications"] = input(
                        "Enable email notifications when GitHub is unavailable? (yes/no): ").lower() == "yes"

                if self.settings["email"]["enable_notifications"]:
                    if not verify_email_settings(self.settings["email"]):
                        while True:
                            print("\nSMTP Settings:")
                            self.settings["email"]["smtp_server"] = input(
                                f"SMTP Server [{self.settings['email'].get('smtp_server', '')}]: ") or self.settings[
                                                                        "email"].get("smtp_server", "")
                            self.settings["email"]["smtp_port"] = int(
                                input(f"SMTP Port [{self.settings['email'].get('smtp_port', 587)}]: ") or self.settings[
                                    "email"].get("smtp_port", 587))
                            self.settings["email"]["sender_email"] = input(
                                f"Sender Email Address [{self.settings['email'].get('sender_email', '')}]: ") or self.settings[
                                                                         "email"].get("sender_email", "")
                            self.settings["email"]["sender_password"] = input("Sender Email Password: ")
                            self.settings["email"]["recipient_email"] = input(
                                f"Recipient Email Address [{self.settings['email'].get('recipient_email', '')}]: ") or \
                                                                        self.settings["email"].get("recipient_email", "")

                            # Verify email settings by sending a test email
                            secret_code = verify_email_settings(self.settings["email"])
                            if not secret_code:
                                print("SMTP settings seem incorrect. Please try again.")
                                continue

                            entered_code = input("Enter the verification code sent to your email: ")
                            if entered_code == secret_code:
                                print("Email verification successful!")
                                break
                            else:
                                print("Incorrect verification code. Please try again.")

            # Save updated settings
            self.save()
        else:
            print("Configuration file already exists. Skipping setup.")


    def test_config(self):
        print("Testing configuration...")
        # Test database connection
        if not test_database_connection(**self.settings["database"]):
            print("Database connection test failed. Please check your settings.")
        # Test GitHub access if bug reporting is enabled
        if self.settings["github"]["create_issues"]:
            if not test_github_access(self.settings["github"]["repo_name"], self.settings["github"]["pat"]):
                print("GitHub access test failed. Please check your settings.")

    def save(self):
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.settings, file, indent=4)
            print(f"Configuration saved to {self.config_file}.")
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get(self, section, key=None, default=None):
        section_data = self.settings.get(section, {})
        if key is None:
            return section_data  # Return the entire section if no key is provided
        return section_data.get(key, default)  # Return a specific key if provided

    @staticmethod
    def get_default_repo():
        try:
            # Run git command to fetch the origin URL
            result = subprocess.run(["git", "config", "--get", "remote.origin.url"],
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            repo_url = result.stdout.strip()
            if repo_url:
                # Extract username and repo name from the URL
                if repo_url.startswith("git@"):  # SSH URL, e.g., git@github.com:username/repo.git
                    repo_path = repo_url.split(':')[1].replace('.git', '')
                elif repo_url.startswith("https://"):  # HTTPS URL, e.g., https://github.com/username/repo.git
                    repo_path = repo_url.split('.com/')[1].replace('.git', '')
                else:
                    return ""
                return repo_path
        except Exception:
            pass
        return ""
