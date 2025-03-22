# modules/config.py
from modules.config_utils import test_database_connection, test_github_access

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
        }
    }

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.settings = {}

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
        print("Let's set up your configuration.")
        self.settings = {"database": {}, "github": {}}

        # Gather and validate database settings
        while True:
            print("\nDatabase Settings:")
            self.settings["database"]["host"] = input("Database Host: ")
            self.settings["database"]["port"] = input("Database Port: ")
            self.settings["database"]["name"] = input("Database Name: ")
            self.settings["database"]["user"] = input("Database User: ")
            self.settings["database"]["password"] = input("Database Password: ")
            if test_database_connection(**self.settings["database"]):
                print("Database connection successful!")
                break
            else:
                print("Database connection failed. Please try again.")

        # Gather and validate GitHub settings
        print("\nGitHub Settings:")
        create_issues = input("Automatically report bugs and exceptions? (yes/no): ").lower() == "yes"
        self.settings["github"]["create_issues"] = create_issues
        while create_issues:
            self.settings["github"]["repo_name"] = input("GitHub Repo Name: ")
            self.settings["github"]["pat"] = input("GitHub Personal Access Token (PAT): ")
            if test_github_access(self.settings["github"]["repo_name"], self.settings["github"]["pat"]):
                print("GitHub access successful!")
                break
            else:
                print("GitHub access failed. Please try again.")

        self.save()

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

    def get(self, section, key, default=None):
        return self.settings.get(section, {}).get(key, default)
