import os
import smtplib
import pandas as pd
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
CSV_FILE = "participants_test.csv"

def load_participants_from_csv(file_path):
    return pd.read_csv(file_path)

def create_email_body_html(participant_name):
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; 
                   line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; 
                    padding: 20px;">
          <h2 style="color: #2c5aa0;">
            Certificate of Appreciation
          </h2>
          <p>Dear <strong>{participant_name}</strong>,</p>
          
          <p>On behalf of the <strong>Emergency Response 
             Group</strong>, we sincerely thank you for your 
             active participation in our <em>Wellness Program</em> 
             last March 19 (Wednesday) at the Engineering 
             Grounds.</p>
          
          <p>We hope the activities not only provided valuable 
             insights into health and wellness but also encouraged 
             you to prioritize your well-being in your daily 
             lives.</p>
          
          <p>Once again, thank you for being part of this 
             journey with us. Let's continue making wellness a 
             priority!</p>
          
          <hr style="border: 1px solid #eee; margin: 20px 0;">
          
          <p style="margin-bottom: 5px;">Best regards,</p>
          <p style="margin: 0;"><strong>Jakim D. Lopez</strong>
             <br>Public Relations Officer
             <br>Emergency Response Group (ERG)</p>
        </div>
      </body>
    </html>
    """
    return html

def create_email_message(sender_email, participant_email,
                          participant_name, cert_path):
    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = participant_email
    message["Subject"] = "Certificate of Appreciation"

    html_body = create_email_body_html(participant_name)
    
    message.add_alternative(html_body, subtype='html')
    
    attach_certificate_to_email(message, cert_path)
    
    return message

def attach_certificate_to_email(message, cert_path):
    if not os.path.exists(cert_path):
        print(f"Certificate file not found: {cert_path}")
        return
    
    with open(cert_path, "rb") as file:
        cert_data = file.read()
        cert_name = os.path.basename(cert_path)
    
    message.add_attachment(
        cert_data,
        maintype="application",
        subtype="jpg",
        filename=cert_name
    )

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
            "certificate_2",
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