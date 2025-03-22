from modules.config import Config

# Initialize and load config
config = Config()
config.load()

# Access specific values
db_user = config.get("database", "user")
print(f"Database User: {db_user}")

if config.get("github", "create_issues"):
    repo_name = config.get("github", "repo_name")
    print(f"Reporting issues to: {repo_name}")
