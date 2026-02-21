import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_API = os.getenv('SMTP_API')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
GMAIL_USER = os.getenv('GMAIL_USER')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

msg = MIMEMultipart()
msg['From'] = formataddr(("Custom Name", GMAIL_USER))
msg['To'] = RECIPIENT_EMAIL

msg['Subject'] = 'Test Email from Python.'

body = 'This is a test email. Stay tuned for more updates!'
msg.attach(MIMEText(body, 'plain'))

def send_test_email():
    try:
        print("Connecting to Gmail SMTP...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.starttls()
        print("Logging in...")
        server.login(GMAIL_USER, SMTP_API)
        print("Sending message...")
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_test_email()