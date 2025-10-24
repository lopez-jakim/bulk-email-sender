import os
import smtplib
import pandas as pd

from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "<input email>"
APP_PASSWORD = "<input app password>"
CSV_FILE = "participants_test.csv"

def load_participants_from_csv(file_path):              # 1st function
        return pd.read_csv(file_path)

def create_email_message(SENDER_EMAIL,                  # 2nd function
                         participant_email, 
                         participant_name, 
                         cert_path):
        message = EmailMessage()
        message["From"] = SENDER_EMAIL
        message["To"] = participant_email
        message["Subject"] = "Certificate of Appreciation"

        body = (f"Dear {participant_name}, <input message>")
        message.set_content(body)

        attach_certificate_to_email(message, cert_path)

        return message

def attach_certificate_to_email(message, cert_path):    # 3rd function
        if not os.path.exists(cert_path):
                print(f"Certificate file not found: {cert_path}")
                return
        
        with open(cert_path, "rb") as file:
                cert_data = file.read()
                cert_name = os.path.basename(cert_path)

        message.add_attachment(cert_data,
                               maintype="application",
                               subtype="pdf",
                               filename=cert_name
                               )

def send_email(message):                                # 4th function
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(message)

        return True
    
    except smtplib.SMTPException as error:
        print(f"Failed to send email: {error}")

        return False

def process_and_send_certificate():                     # 5th and main function
        participants = load_participants_from_csv(CSV_FILE)
        successful_emails = 0  
        total_emails = 0  

        for _, row in participants.iterrows():
                participant_name = row["Name"]
                participant_email = row["Email"]
                cert_path = os.path.join("certificates", 
                                         row["Certificate File"])
                total_emails += 1                       # add email attemps (it can be fail or success)

                if not os.path.exists(cert_path):
                        print(f"Certificate missing for {participant_name}")
                        continue
                
                email_message = create_email_message(SENDER_EMAIL,
                                                     participant_email,
                                                     participant_name,
                                                     cert_path)
                
                success = send_email(email_message)

                if success:
                        successful_emails += 1
                        # add counter for successful emails
                        print(f"Email sent to {participant_name}"
                                + f" <{participant_email}>")
                else:
                        print(f"Email failed for {participant_name}"
                                + f" <{participant_email}>")
                                
                print(f"\nSummary: {successful_emails} email(s) sent"
                        + f" successfully out of {total_emails} attempted.\n")

process_and_send_certificate()