import json
import requests
import mysql.connector
from mysql.connector import Error
import random
from modules.mail import send_email

def test_database_connection(host, port, user, password, name):
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=name  # Ensure the correct parameter is used here
        )
        if connection.is_connected():
            connection.close()
            return True
    except mysql.connector.Error as e:
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

def verify_email_settings(settings):
    print("\nVerifying email settings...")

    # Generate a random secret code
    secret_code = str(random.randint(100000, 999999))
    subject = "Email Verification"
    body = f"Your verification code is: {secret_code}"

    try:
        # Use the `send_email` function from modules/mail.py
        send_email(
            smtp_server=settings["smtp_server"],
            smtp_port=settings["smtp_port"],
            sender_email=settings["sender_email"],
            sender_password=settings["sender_password"],
            recipient_email=settings["recipient_email"],
            subject=subject,
            body=body
        )
        print("Verification email sent. Please check your inbox.")
        return secret_code
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return None

def verify_fio_api_key(api_key):
    """Verify the FIO API key using the FIO auth endpoint."""
    try:
        response = requests.get(
            "https://rest.fnar.net/auth",
            headers={"accept": "application/json", "Authorization": api_key},
            timeout=5  # Add a timeout to avoid hanging
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error verifying FIO API key: {e}")
        return False