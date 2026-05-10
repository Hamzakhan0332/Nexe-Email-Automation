import os
import time
import base64
import csv
from datetime import datetime
from email.message import EmailMessage

import schedule
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
LOG_FILE = "nexe_email_log.csv"

SCHEDULED_EMAILS = [
    {
        "time": "17:01",
        "recipient": "jutitori@gmail.com",
        "subject": "Morning Update - Nexe Automation",
        "body": "Good morning! This is your scheduled automated email from Nexe."
    },
    {
        "time": "17:02",
        "recipient": "70147584@student.uol.edu.pk",
        "subject": "Evening Report - Nexe Automation",
        "body": "Good evening! Here is your daily automated report."
    }
]


def prompt_for_schedules():
    """Prompt the user in terminal to enter scheduled emails.
    User can press Enter at the time prompt to finish entering schedules.
    Returns a list of schedule dicts matching the SCHEDULED_EMAILS format.
    """
    schedules = []
    print('\nEnter scheduled emails. To stop, leave the time empty and press Enter.')

    while True:
        time_input = input('Time (HH:MM): ').strip()
        if not time_input:
            break

        # Basic validation for HH:MM
        try:
            datetime.strptime(time_input, '%H:%M')
        except ValueError:
            print('Invalid time format. Please use HH:MM (24-hour).')
            continue

        recipient = input('Recipient email: ').strip()
        if not recipient:
            print('Recipient cannot be empty.')
            continue

        subject = input('Subject: ').strip()
        body = input('Body: ').strip()

        schedules.append({
            'time': time_input,
            'recipient': recipient,
            'subject': subject or '(no subject)',
            'body': body or ''
        })

        print('Scheduled entry added. Add another or press Enter at Time to finish.')

    return schedules

def authenticate_gmail():
    creds = None
    
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error reading token.json: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing expired token...")
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                creds = None
                
        if not creds:
            try:
                print("Opening browser for Google Account login...")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("Error: 'credentials.json' file not found.")
                return None
            except Exception as e:
                print(f"Authentication error: {e}")
                return None

        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("Login successful.")
        except Exception as e:
            print(f"Could not save token.json: {e}")

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build Gmail service: {e}")
        return None

def log_email(recipient, subject, status, error_message="None"):
    file_exists = os.path.isfile(LOG_FILE)
    
    try:
        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(['timestamp', 'recipient', 'subject', 'status', 'error_message'])
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, recipient, subject, status, error_message])
    except Exception as e:
        print(f"Could not write to log file: {e}")

def send_email(service, recipient, subject, body):
    if not service:
        print("Cannot send email: Not authenticated.")
        log_email(recipient, subject, "Failed", "Not authenticated")
        return

    try:
        print(f"Sending email to {recipient}...")
        
        message = EmailMessage()
        message.set_content(body)
        message['To'] = recipient
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        service.users().messages().send(userId="me", body=create_message).execute()
        
        print(f"Successfully sent email to {recipient}")
        log_email(recipient, subject, "Success")
        
    except HttpError as error:
        error_msg = f"Gmail API Error: {error}"
        print(error_msg)
        log_email(recipient, subject, "Failed", error_msg)
    except Exception as e:
        error_msg = f"Unexpected Error: {e}"
        print(error_msg)
        log_email(recipient, subject, "Failed", error_msg)

def schedule_job(email_data):
    service = authenticate_gmail()
    
    send_email(
        service=service,
        recipient=email_data["recipient"],
        subject=email_data["subject"],
        body=email_data["body"]
    )

def setup_schedules():
    print("\nSetting up email schedule...")
    for email_data in SCHEDULED_EMAILS:
        time_to_send = email_data["time"]
        recipient = email_data["recipient"]
        
        schedule.every().day.at(time_to_send).do(schedule_job, email_data)
        
        print(f"Scheduled email to {recipient} at {time_to_send}")

def main():
    print("=" * 40)
    print("     NEXE EMAIL AUTOMATION STARTED")
    print("=" * 40)
    
    print("\nChecking Gmail connection...")
    service = authenticate_gmail()
    if service:
        print("Connection ready.")
    else:
        print("Could not connect. Check credentials.json.")
        
    # Offer interactive input to override the hard-coded schedules
    try:
        use_prompt = input('\nWould you like to enter scheduled emails manually? (y/N): ').strip().lower()
    except Exception:
        use_prompt = 'n'

    if use_prompt == 'y':
        user_schedules = prompt_for_schedules()
        if user_schedules:
            global SCHEDULED_EMAILS
            SCHEDULED_EMAILS = user_schedules
            print(f"Using {len(SCHEDULED_EMAILS)} user-provided schedule(s).")
        else:
            print('No schedules entered; using default schedules.')

    setup_schedules()
    
    print("\nWaiting for scheduled times...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nAutomation stopped.")

if __name__ == '__main__':
    main()
