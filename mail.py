import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import markdown
from dotenv import load_dotenv
load_dotenv()

SENT_LOG_FILE = Path("sent_summaries.json")
QUEUE_FILE = Path("summary_queue.json")

def load_sent_log():
    if SENT_LOG_FILE.exists():
        with open(SENT_LOG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_sent_log(log_data):
    with open(SENT_LOG_FILE, 'w') as f:
        json.dump(log_data, indent=2, fp=f)

def load_queue():
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {"queue": [], "sent_order": []}

def save_queue(queue_data):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue_data, indent=2, fp=f)

def get_summary_hash(content):
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()

def get_all_summaries():
    """Get all SUMMARY.md files with their metadata."""
    docs_dir = Path("github_docs")
    if not docs_dir.exists():
        return {}
    
    summaries = {}
    for summary_file in docs_dir.rglob("SUMMARY.md"):
        repo_name = summary_file.parent.name
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
        summaries[repo_name] = {
            "path": str(summary_file),
            "hash": get_summary_hash(content),
            "content": content,
            "modified_at": summary_file.stat().st_mtime
        }
    return summaries

def build_queue():
    """Build/update the send queue based on available summaries."""
    all_summaries = get_all_summaries()
    queue_data = load_queue()

    existing_queue = queue_data.get("queue", [])
    sent_order = queue_data.get("sent_order", [])

    existing_queue_repos = {item["repo_name"] for item in existing_queue}
    all_repo_names = set(all_summaries.keys())

    # Detect new repos not in queue or sent_order
    new_repos = all_repo_names - existing_queue_repos - set(sent_order)

    # Add new repos to front of queue
    new_entries = [
        {"repo_name": r, "added_at": datetime.now().isoformat()}
        for r in sorted(new_repos, key=lambda r: all_summaries[r]["modified_at"], reverse=True)
    ]

    final_queue = new_entries + existing_queue

    # If queue is empty, start new cycle with all repos
    if not final_queue:
        print("Queue empty - starting new cycle with all repos.")
        sent_order_repos = [r for r in sent_order if r in all_summaries]
        final_queue = [
            {"repo_name": r, "added_at": datetime.now().isoformat()}
            for r in sent_order_repos
        ]
        sent_order.clear()
    
    queue_data["queue"] = final_queue
    queue_data["sent_order"] = sent_order
    save_queue(queue_data)

    print(f"Queue status: {len(final_queue)} repos pending")
    if new_repos:
        print(f"New repos: {list(new_repos)}")

    return queue_data


def get_next_to_send():
    """Get the next repo from queue to send."""
    all_summaries = get_all_summaries()
    queue_data = build_queue()
    queue = queue_data.get("queue", [])

    if not queue:
        print("No summaries to send.")
        return None, None, queue_data

    next_item = queue[0]
    repo_name = next_item["repo_name"]

    if repo_name not in all_summaries:
        print(f"Repo {repo_name} not found, skipping.")
        queue_data["queue"].pop(0)
        save_queue(queue_data)
        return None, None, queue_data

    return all_summaries[repo_name]["content"], repo_name, queue_data

def enhance_markdown_content(content: str) -> str:
    """Enhance markdown content with special formatting."""
    lines = content.split('\n')
    enhanced_lines = []
    in_feature_section = False
    
    for line in lines:
        # Add icons to main sections
        if line.startswith('## 1. Project Overview'):
            line = '## 🎯 Project Overview & Purpose'
        elif line.startswith('## 2. Key Features'):
            line = '## ⚡ Key Features & Capabilities'
            in_feature_section = True
        elif line.startswith('## 3. Architecture'):
            line = '## 🏗️ Architecture & Technical Design'
            in_feature_section = False
        elif line.startswith('## 4.') or line.startswith('## 5.'):
            in_feature_section = False
        
        # Enhance "What it does" style sections
        if '**What it does**:' in line:
            line = '<div class="info-box">💡 <strong>What it does:</strong> ' + line.split('**What it does**:')[1]
        elif '**Why it\'s useful**:' in line or "**Why it's useful**:" in line:
            line = '</div><div class="info-box">✨ <strong>Why it\'s useful:</strong> ' + line.split(':')[1]
        elif '**When to use it**:' in line:
            line = '</div><div class="info-box">🎯 <strong>When to use it:</strong> ' + line.split('**When to use it**:')[1]
        elif '**Limitations**:' in line:
            line = '</div><div class="warning-box">⚠️ <strong>Limitations:</strong> ' + line.split('**Limitations**:')[1] + '</div>'
        
        # Add icons to subsections
        if line.startswith('### What is this project'):
            line = '### 📖 What is this project and what problem does it solve?'
        elif line.startswith('### Target audience'):
            line = '### 👥 Target audience and use cases'
        elif line.startswith('### Project history'):
            line = '### 📅 Project history, maturity, and current status'
        elif line.startswith('### Key differentiators'):
            line = '### 🌟 Key differentiators from similar projects'
        elif line.startswith('### Major Features'):
            line = '### 🚀 Major Features'
        elif line.startswith('### Overall system architecture'):
            line = '### 🔧 Overall system architecture'
        elif line.startswith('### Design patterns'):
            line = '### 🎨 Design patterns and principles used'
        elif line.startswith('### Data flow'):
            line = '### 🔄 Data flow and component interactions'
        
        enhanced_lines.append(line)
    
    return '\n'.join(enhanced_lines)

def create_html_email(summary_content: str, repo_name: str, queue_position: int, queue_total: int) -> str:
    """Create an attractive HTML email with improved styling."""
    
    enhanced_content = enhance_markdown_content(summary_content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        enhanced_content,
        extensions=['extra', 'codehilite', 'tables', 'toc']
    )
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 14px;
            }}
            .progress {{
                background: rgba(255,255,255,0.2);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 13px;
                margin-top: 10px;
                display: inline-block;
            }}
            .content {{
                padding: 40px;
            }}
            .repo-badge {{
                display: inline-block;
                background-color: #f0f0f0;
                color: #333;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #1a202c;
                font-size: 24px;
                margin-top: 30px;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }}
            h2 {{
                color: #2d3748;
                font-size: 20px;
                margin-top: 25px;
                margin-bottom: 12px;
                padding-left: 10px;
                border-left: 4px solid #667eea;
            }}
            h3 {{
                color: #4a5568;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            h4 {{
                color: #667eea;
                font-size: 16px;
                margin-top: 15px;
                margin-bottom: 8px;
            }}
            ul, ol {{
                margin: 10px 0;
                padding-left: 25px;
            }}
            li {{
                margin: 8px 0;
            }}
            code {{
                background-color: #f7fafc;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                color: #e53e3e;
            }}
            pre {{
                background-color: #2d3748;
                color: #f7fafc;
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
                margin: 15px 0;
            }}
            pre code {{
                background-color: transparent;
                color: inherit;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #667eea;
                padding-left: 20px;
                margin: 20px 0;
                color: #4a5568;
                background-color: #f7fafc;
                padding: 15px 20px;
                border-radius: 4px;
            }}
            .info-box {{
                background-color: #ebf8ff;
                border-left: 4px solid #4299e1;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }}
            .warning-box {{
                background-color: #fffaf0;
                border-left: 4px solid #f6ad55;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }}
            .success-box {{
                background-color: #f0fff4;
                border-left: 4px solid #48bb78;
                padding: 15px;
                margin: 15px 0;
                border-radius: 4px;
            }}
            .footer {{
                background-color: #f7fafc;
                padding: 20px 40px;
                text-align: center;
                color: #718096;
                font-size: 14px;
                border-top: 1px solid #e2e8f0;
            }}
            .footer a {{
                color: #667eea;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            hr {{
                border: none;
                border-top: 1px solid #e2e8f0;
                margin: 30px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }}
            th {{
                background-color: #f7fafc;
                font-weight: 600;
                color: #2d3748;
            }}
            strong {{
                color: #2d3748;
            }}
            em {{
                color: #4a5568;
                font-style: italic;
            }}
            .divider {{
                height: 2px;
                background: linear-gradient(to right, transparent, #667eea, transparent);
                margin: 30px 0;
                border: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📚 Daily Documentation Summary</h1>
                <p>{datetime.now().strftime("%B %d, %Y")}</p>
                <div class="progress">📬 Repo {queue_position} of {queue_total}</div>
            </div>
            <div class="content">
                <div class="repo-badge">🔖 Repository: {repo_name}</div>
                <hr class="divider">
                {html_content}
            </div>
            <div class="footer">
                <p>🤖 Auto-generated by GitHub Actions</p>
                <p><a href="https://github.com/{repo_name}">📂 View Repository</a></p>
                <p style="margin-top: 10px; font-size: 12px;">Generated with ❤️ by your documentation automation system</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email(subject: str, html_content: str):
    """Send email using SMTP."""
    smtp_api = os.getenv('SMTP_API')
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    gmail_user = os.getenv('GMAIL_USER')
    recipient = os.getenv('RECIPIENT_EMAIL')
    
    if not all([smtp_api, smtp_host, gmail_user, recipient]):
        print("Missing required environment variables for email")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = recipient
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(gmail_user, smtp_api)
            server.send_message(msg)
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def main():
    print("Starting daily email summary task...")

    summary_content, repo_name, queue_data = get_next_to_send()

    if not summary_content or not repo_name:
        print("Nothing to send today.")
        return

    queue = queue_data.get("queue", [])
    sent_order = queue_data.get("sent_order", [])
    total_cycle = len(queue) + len(sent_order)
    position = len(sent_order) + 1

    print(f"Sending summary for: {repo_name} ({position}/{total_cycle})")

    html_content = create_html_email(summary_content, repo_name, position, total_cycle)
    subject = f"📚 Doc Summary [{position}/{total_cycle}]: {repo_name}"

    if send_email(subject, html_content):
        # Update queue and sent_order
        queue_data["queue"] = [i for i in queue if i["repo_name"] != repo_name]
        queue_data["sent_order"].append(repo_name)
        save_queue(queue_data)
        
        # Log as sent
        sent_log = load_sent_log()
        sent_log[repo_name] = {
            "hash": get_summary_hash(summary_content),
            "sent_at": datetime.now().isoformat(),
        }
        save_sent_log(sent_log)

        print(f"Sent and logged: {repo_name}")
    else:
        print(f"Failed to send: {repo_name}")

if __name__ == "__main__":
    main()