import requests
import random
import time
import string
import json  # Import the json module for pretty printing

# Base URL for the Mail TM API
BASE_URL = "https://api.mail.tm"

# Function to get available domains
def get_domains():
    response = requests.get(f"{BASE_URL}/domains")
    if response.status_code == 200:
        domains = response.json().get("hydra:member", [])
        if domains:
            return [domain['domain'] for domain in domains]
        else:
            print("No domains available.")
            return None
    else:
        print(f"Failed to fetch domains: {response.text}")
        return None

# Function to generate a random username
def generate_random_username(length=8):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Function to create a random email with a valid domain
def create_random_email():
    domains = get_domains()
    if not domains:
        return None
    
    random_domain = random.choice(domains)
    random_username = generate_random_username()
    email_address = f"{random_username}@{random_domain}"
    password = "StrongPassword123!"
    
    response = requests.post(f"{BASE_URL}/accounts", json={
        "address": email_address,
        "password": password
    })
    
    if response.status_code == 201:
        print(f"Email account created successfully: {email_address}")
        return {
            "address": email_address,
            "password": password
        }
    else:
        print(f"Failed to create email account: {response.text}")
        return None

# Function to get a token for the created email
def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", json={
        "address": email,
        "password": password
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"Failed to get token: {response.text}")
        return None

# Function to get messages from the mailbox
def get_messages(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    
    if response.status_code == 200:
        return response.json().get("hydra:member", [])
    else:
        print(f"Failed to get messages: {response.text}")
        return None

# Main function to create email, get token, and receive messages
def main():
    account = create_random_email()
    if account:
        email = account['address']
        password = account['password']
        
        # Wait for a moment before attempting to fetch the token
        time.sleep(2)
        
        token = get_token(email, password)
        if token:
            print(f"Token received: {token}")
            
            # Wait up to 60 seconds for messages, checking every 5 seconds
            timeout = 60  # total time to wait in seconds
            interval = 5  # time between checks in seconds
            elapsed_time = 0
            
            while elapsed_time < timeout:
                messages = get_messages(token)
                
                # Pretty print the entire messages data structure
                print("Messages data structure (pretty JSON):")
                print(json.dumps(messages, indent=4))  # Pretty print with indent
                
                if messages:
                    print(f"Received {len(messages)} messages:")
                    for message in messages:
                        print(f"From: {message['from']['address']}")
                        print(f"Subject: {message['subject']}")
                        
                        # Safely retrieve the 'text' or 'html' content
                        if 'text' in message:
                            print(f"Text: {message['text']}\n")
                        elif 'html' in message:
                            print(f"HTML: {message['html']}\n")
                        else:
                            print("No text or HTML content available.\n")
                    break
                else:
                    print("No messages yet, checking again in 5 seconds...")
                    time.sleep(interval)
                    elapsed_time += interval
            else:
                print("No messages received within 60 seconds.")
        else:
            print("Failed to receive token.")
    else:
        print("Failed to create account.")

if __name__ == "__main__":
    main()
