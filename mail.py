import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from dotenv import load_dotenv
from pathlib import Path
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Email configuration
SMTP_API = os.getenv('SMTP_API')
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
GMAIL_USER = os.getenv('GMAIL_USER')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Path configuration
DOCS_DIR = Path('./github_docs')
SENT_LOG_FILE = Path('./sent_summaries.json')

def load_sent_log():
    """Load the log of sent summaries."""
    if SENT_LOG_FILE.exists():
        with open(SENT_LOG_FILE, 'r') as f:
            return json.load(f)
    return {"sent": [], "timestamp": {}}

def save_sent_log(log_data):
    """Save the log of sent summaries."""
    with open(SENT_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

def get_all_summaries():
    """Get all SUMMARY.md files from github_docs."""
    summaries = []
    for summary_path in DOCS_DIR.rglob('SUMMARY.md'):
        repo_name = summary_path.parent.name
        summaries.append({
            'repo_name': repo_name,
            'path': summary_path
        })
    return summaries

def get_next_summary_to_send():
    """Get the next summary to send in cyclic order."""
    all_summaries = get_all_summaries()
    
    if not all_summaries:
        logging.warning("No summaries found!")
        return None
    
    sent_log = load_sent_log()
    sent_repos = set(sent_log.get('sent', []))
    
    # Get all repo names
    all_repo_names = {s['repo_name'] for s in all_summaries}
    
    # Find unsent summaries
    unsent_summaries = [s for s in all_summaries if s['repo_name'] not in sent_repos]
    
    # If all summaries have been sent, reset the cycle
    if not unsent_summaries:
        logging.info("All summaries have been sent. Restarting cycle...")
        sent_log['sent'] = []
        save_sent_log(sent_log)
        unsent_summaries = all_summaries
    
    # Sort to ensure consistent ordering
    unsent_summaries.sort(key=lambda x: x['repo_name'])
    
    return unsent_summaries[0] if unsent_summaries else None

def send_summary_email(summary_info):
    """Send a summary via email."""
    repo_name = summary_info['repo_name']
    summary_path = summary_info['path']
    
    try:
        # Read the summary content
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = formataddr(("GitHub Docs Bot", GMAIL_USER))
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"📚 Daily Documentation: {repo_name}"
        
        # Create email body
        email_body = f"""
Hello!

Here's today's documentation summary for the repository: {repo_name}

{'-' * 80}

{summary_content}

{'-' * 80}

This is an automated email sent as part of your daily GitHub documentation digest.

Repository: {repo_name}
Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
GitHub Docs Bot
"""
        
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        
        # Send email
        logging.info(f"Connecting to SMTP server {SMTP_HOST}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.starttls()
        
        logging.info("Logging in...")
        server.login(GMAIL_USER, SMTP_API)
        
        logging.info(f"Sending email for {repo_name}...")
        server.send_message(msg)
        server.quit()
        
        logging.info(f"✅ Email sent successfully for {repo_name}!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to send email for {repo_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def mark_as_sent(repo_name):
    """Mark a summary as sent in the log."""
    sent_log = load_sent_log()
    
    if repo_name not in sent_log['sent']:
        sent_log['sent'].append(repo_name)
    
    sent_log['timestamp'][repo_name] = datetime.now().isoformat()
    
    save_sent_log(sent_log)
    logging.info(f"Marked {repo_name} as sent")

def send_daily_summary():
    """Main function to send one summary per day."""
    logging.info("Starting daily summary email process...")
    
    # Get next summary to send
    summary_info = get_next_summary_to_send()
    
    if not summary_info:
        logging.warning("No summaries available to send!")
        return False
    
    repo_name = summary_info['repo_name']
    logging.info(f"Selected summary: {repo_name}")
    
    # Send the email
    success = send_summary_email(summary_info)
    
    if success:
        # Mark as sent
        mark_as_sent(repo_name)
        
        # Show statistics
        sent_log = load_sent_log()
        all_summaries = get_all_summaries()
        logging.info(f"\n📊 Statistics:")
        logging.info(f"   Total summaries: {len(all_summaries)}")
        logging.info(f"   Sent this cycle: {len(sent_log['sent'])}")
        logging.info(f"   Remaining: {len(all_summaries) - len(sent_log['sent'])}")
        
        return True
    
    return False

if __name__ == "__main__":
    send_daily_summary()