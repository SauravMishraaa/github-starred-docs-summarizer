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

def get_latest_summary():
    """Find and return the most recently modified SUMMARY.md file."""
    docs_dir = Path("github_docs")
    if not docs_dir.exists():
        return None, None
    
    summary_files = list(docs_dir.rglob("SUMMARY.md"))
    if not summary_files:
        return None, None
    
    latest_file = max(summary_files, key=lambda p: p.stat().st_mtime)
    repo_name = latest_file.parent.name
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content, repo_name

def load_sent_log():
    """Load the log of sent summaries."""
    log_file = Path("sent_summaries.json")
    if log_file.exists():
        with open(log_file, 'r') as f:
            return json.load(f)
    return {}

def save_sent_log(log_data):
    """Save the log of sent summaries."""
    with open("sent_summaries.json", 'w') as f:
        json.dump(log_data, indent=2, fp=f)

def get_summary_hash(content):
    """Create a simple hash of the summary content."""
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()

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

def create_html_email(summary_content: str, repo_name: str) -> str:
    """Create an attractive HTML email with improved styling."""
    
    # Enhance the markdown content
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
    
    # Get the latest summary
    summary_content, repo_name = get_latest_summary()
    
    if not summary_content:
        print("No summary files found")
        return
    
    # Check if we've already sent this summary
    sent_log = load_sent_log()
    content_hash = get_summary_hash(summary_content)
    
    if repo_name in sent_log and sent_log[repo_name].get('hash') == content_hash:
        print(f"Summary for {repo_name} already sent. Skipping.")
        return
    
    print(f"Found new summary for repository: {repo_name}")
    
    # Create HTML email
    html_content = create_html_email(summary_content, repo_name)
    
    # Send email
    subject = f"📚 Daily Documentation Summary: {repo_name}"
    if send_email(subject, html_content):
        # Update sent log
        sent_log[repo_name] = {
            'hash': content_hash,
            'sent_at': datetime.now().isoformat(),
            'date': datetime.now().strftime("%Y-%m-%d")
        }
        save_sent_log(sent_log)
        print("Sent log updated")
    else:
        print("Failed to send email")

if __name__ == "__main__":
    main()