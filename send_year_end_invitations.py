import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("AWS_SENDER_EMAIL")
APP_PASSWORD = os.getenv("AWS_APP_PASSWORD")
CSV_FILE = "year_end_party_recipients.csv"
EMAIL_TEMPLATE_FILE = "FOR-INTERNALS-FINAL.html"

def load_participants_from_csv(file_path):
    return pd.read_csv(file_path)

def create_email_body_html(row):
    """Create email body by replacing all merge tags with participant data"""
    with open(EMAIL_TEMPLATE_FILE, "r", encoding="utf-8") as file:
        html = file.read()
    
    # Replace all merge tags with actual values from CSV
    html = html.replace("{{ NAME }}", str(row["NAME"]))
    html = html.replace("{{ NICKNAME }}", str(row["NICKNAME"]))
    html = html.replace("{{ DEPARTMENT }}", str(row["DEPARTMENT"]))
    html = html.replace("{{ ROLE }}", str(row["ROLE"]))
    html = html.replace("{{ AWS_ID }}", str(row["AWS_ID"]))

    return html

def create_email_message(sender_email, participant_email, participant_row):
    """Create email message with HTML body"""
    msg = MIMEMultipart('related')
    msg["From"] = sender_email
    msg["To"] = participant_email
    msg["Subject"] = "🎉 You're Invited: AWSCC Year-End Celebration - Beyond the Horizon"

    html_body = create_email_body_html(participant_row)
    msg.attach(MIMEText(html_body, 'html'))
    
    return msg

def send_email(message):
    """Send email via SMTP"""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(message)
        return True
    except smtplib.SMTPException as error:
        print(f"Failed to send email: {error}")
        return False

def send_year_end_invitations():
    """Process CSV and send personalized invitations"""
    participants = load_participants_from_csv(CSV_FILE)
    successful_emails = 0
    total_emails = 0
    
    print("=" * 60)
    print("AWS Cloud Club - Year-End Party Invitation Sender")
    print("=" * 60)
    print(f"\nLoading participants from: {CSV_FILE}")
    print(f"Using template: {EMAIL_TEMPLATE_FILE}\n")
    
    for _, row in participants.iterrows():
        participant_name = row["NAME"]
        participant_email = row["EMAIL"]
        total_emails += 1
        
        print(f"Preparing email for {participant_name} ({row.get('NICKNAME', 'N/A')})...")
        
        email_message = create_email_message(
            SENDER_EMAIL,
            participant_email,
            row
        )
        
        success = send_email(email_message)
        
        if success:
            successful_emails += 1
            print(f"✅ Email sent successfully to {participant_name} <{participant_email}>")
        else:
            print(f"❌ Email failed for {participant_name} <{participant_email}>")
        
        print("-" * 60)
    
    print(f"\n{'=' * 60}")
    print(f"📊 Summary: {successful_emails}/{total_emails} emails sent successfully")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    send_year_end_invitations()
