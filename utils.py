from passlib.hash import sha256_crypt
import json
import os
import smtplib
from email.mime.text import MIMEText
import re


# Define constants
USERS_FILE = 'users.json'

# Function to load users from a JSON file
def load_users(file=USERS_FILE):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

# Function to save user with a hashed password
def save_user(username, password, file=USERS_FILE):
    users = load_users(file)
    # Hash password using sha256_crypt before saving
    users[username] = sha256_crypt.hash(password)
    with open(file, 'w') as f:
        json.dump(users, f)
    print(f"User '{username}' added successfully.")

# Function to verify password for an existing user
def verify_password(username, password, file=USERS_FILE):
    users = load_users(file)
    if username in users:
        # Check if the hashed password matches
        return sha256_crypt.verify(password, users[username])
    return False

# Function to validate email format
def validate_email(email):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_regex, email) is not None

# Function to send an email alert
def send_email(to_email, subject, message, from_email='your_email@gmail.com', password='your_password'):
    if not validate_email(to_email):
        raise ValueError("Invalid email address format.")
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection
            server.login(from_email, password)
            server.send_message(msg)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
