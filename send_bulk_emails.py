import os
import smtplib
import pandas as pd
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
CSV_FILE = "participants_test.csv"
EMAIL_TEMPLATE_FILE = "erg_ga_email_template.html"
BANNER_IMAGE_FILE = "erg_banner.png"

def load_participants_from_csv(file_path):
    return pd.read_csv(file_path)

def create_email_body_html(participant_name):
  with open(EMAIL_TEMPLATE_FILE, "r", encoding="utf-8") as file:
    html = file.read()
  
  # Replace placeholders
  html = html.replace("{participant_name}", participant_name)
  html = html.replace("{erg_banner}", "cid:erg_banner")
  
  return html

def create_email_message(sender_email, participant_email,
                          participant_name, cert_path):
    msg = MIMEMultipart('related')
    msg["From"] = sender_email
    msg["To"] = participant_email
    msg["Subject"] = "Certificate of Appreciation"

    html_body = create_email_body_html(participant_name)
    
    msg.attach(MIMEText(html_body, 'html'))
    
    # Attach ERG banner as inline image with CID
    with open(BANNER_IMAGE_FILE, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<erg_banner>')
        img.add_header('Content-Disposition', 'inline', 
                       filename='erg_banner.png')
        msg.attach(img)
    
    # Attach certificate
    attach_certificate_to_email(msg, cert_path)
    
    return msg

def attach_certificate_to_email(message, cert_path):
    if not os.path.exists(cert_path):
        print(f"Certificate file not found: {cert_path}")
        return
    
    with open(cert_path, "rb") as file:
        cert_data = file.read()
        cert_name = os.path.basename(cert_path)
    
    part = MIMEBase("application", "octet-stream")
    part.set_payload(cert_data)
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {cert_name}"
    )
    message.attach(part)

def send_email(message):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(message)
        return True
    except smtplib.SMTPException as error:
        print(f"Failed to send email: {error}")
        return False

def process_and_send_certificate():
    participants = load_participants_from_csv(CSV_FILE)
    successful_emails = 0
    total_emails = 0
    
    for _, row in participants.iterrows():
        participant_name = row["Name"]
        participant_email = row["Email"]
        cert_path = os.path.join(
            "certificates_2",
            row["Certificate File"]
        )
        total_emails += 1
        
        if not os.path.exists(cert_path):
            print(f"Certificate missing for {participant_name}")
            continue
        
        email_message = create_email_message(
            SENDER_EMAIL,
            participant_email,
            participant_name,
            cert_path
        )
        
        success = send_email(email_message)
        
        if success:
            successful_emails += 1
            print(
                f"Email sent to {participant_name} "
                + f"<{participant_email}>"
            )
        else:
            print(
                f"Email failed for {participant_name} "
                + f"<{participant_email}>"
            )
    
    print(
        f"\nSummary: {successful_emails} email(s) sent "
        + f"successfully out of {total_emails} attempted.\n"
    )

if __name__ == "__main__":
    process_and_send_certificate()