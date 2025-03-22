import json
import requests
import mysql.connector
from mysql.connector import Error

def test_database_connection(host, port, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            connection.close()
            return True
    except Error as e:
        print(f"Database connection failed: {e}")
    return False

def test_github_access(repo_name, pat):
    try:
        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com/repos/{repo_name}"
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"GitHub access failed: {e}")
    return False
