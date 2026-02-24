import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
import markdown

load_dotenv()

SENT_LOG_FILE = Path("sent_summaries_telegram.json")
QUEUE_FILE = Path("summary_queue_telegram.json")

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

    new_repos = all_repo_names - existing_queue_repos - set(sent_order)

    new_entries = [
        {"repo_name": r, "added_at": datetime.now().isoformat()}
        for r in sorted(new_repos, key=lambda r: all_summaries[r]["modified_at"], reverse=True)
    ]

    final_queue = new_entries + existing_queue

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
        return None, None, None

    next_item = queue[0]
    repo_name = next_item["repo_name"]

    if repo_name not in all_summaries:
        print(f"Repo {repo_name} not found, skipping.")
        queue_data["queue"].pop(0)
        save_queue(queue_data)
        return None, None, None

    return all_summaries[repo_name]["content"], repo_name, queue_data

def markdown_to_telegram(content: str) -> str:
    """Convert markdown to Telegram's MarkdownV2 format."""
    # Telegram MarkdownV2 requires escaping special characters
    # but we need to preserve markdown formatting
    
    lines = content.split('\n')
    telegram_lines = []
    
    for line in lines:
        # Convert headers
        if line.startswith('# '):
            telegram_lines.append('*' + line[2:].strip() + '*')
        elif line.startswith('## '):
            telegram_lines.append('*' + line[3:].strip() + '*')
        elif line.startswith('### '):
            telegram_lines.append('*' + line[4:].strip() + '*')
        elif line.startswith('#### '):
            telegram_lines.append('*' + line[5:].strip() + '*')
        # Convert bold
        elif '**' in line:
            line = line.replace('**', '*')
            telegram_lines.append(line)
        # Convert code blocks
        elif line.startswith('```'):
            telegram_lines.append(line)
        else:
            telegram_lines.append(line)
    
    return '\n'.join(telegram_lines)

def split_message(text: str, max_length: int = 4096) -> list:
    """Split long messages into chunks that fit Telegram's limit."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    for line in text.split('\n'):
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def send_telegram_message(message: str, bot_token: str, chat_id: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Split message if too long
    chunks = split_message(message)
    
    success = True
    for i, chunk in enumerate(chunks):
        if len(chunks) > 1:
            # Add part indicator for multi-part messages
            if i == 0:
                chunk = f"📄 *Part {i+1}/{len(chunks)}*\n\n{chunk}"
            else:
                chunk = f"📄 *Part {i+1}/{len(chunks)} (continued)*\n\n{chunk}"
        
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            print(f"Telegram message part {i+1}/{len(chunks)} sent successfully")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Telegram message part {i+1}: {e}")
            success = False
            break
    
    return success

def send_telegram_document(content: str, filename: str, bot_token: str, chat_id: str, caption: str = "") -> bool:
    """Send content as a document file via Telegram."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    files = {
        'document': (filename, content.encode('utf-8'), 'text/markdown')
    }
    
    data = {
        'chat_id': chat_id,
        'caption': caption,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        response.raise_for_status()
        print(f"Telegram document sent successfully: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram document: {e}")
        return False

def format_summary_header(repo_name: str, queue_position: int, queue_total: int) -> str:
    """Create a formatted header for the summary."""
    header = f"""
📚 *Daily Documentation Summary*
📅 {datetime.now().strftime("%B %d, %Y")}

🔖 *Repository:* `{repo_name}`
📊 *Progress:* {queue_position}/{queue_total} sent

━━━━━━━━━━━━━━━━━━━━
"""
    return header.strip()

def create_telegram_summary(content: str, repo_name: str, queue_position: int, queue_total: int) -> str:
    """Create a Telegram-formatted summary."""
    header = format_summary_header(repo_name, queue_position, queue_total)
    
    # Convert markdown content
    telegram_content = markdown_to_telegram(content)
    
    footer = f"""

━━━━━━━━━━━━━━━━━━━━
🤖 Auto-generated by GitHub Actions
🔗 [View Repository](https://github.com/{repo_name})
"""
    
    return header + "\n\n" + telegram_content + footer

def send_summary_to_telegram(summary_content: str, repo_name: str) -> bool:
    """Send summary to Telegram (both as message and document)."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    
    # Send as document (full content, always works)
    filename = f"{repo_name}_summary_{datetime.now().strftime('%Y%m%d')}.md"
    caption = f"📚 Documentation Summary: *{repo_name}*"
    
    doc_success = send_telegram_document(
        summary_content, 
        filename, 
        bot_token, 
        chat_id, 
        caption
    )
    
    # Also try to send formatted message (if not too long)
    queue_data = load_queue()
    queue_total = len(queue_data.get("sent_order", [])) + len(queue_data.get("queue", []))
    queue_position = len(queue_data.get("sent_order", [])) + 1
    
    telegram_summary = create_telegram_summary(
        summary_content, 
        repo_name, 
        queue_position, 
        queue_total
    )
    
    # If summary is short enough, send as message too
    if len(telegram_summary) < 3000:
        msg_success = send_telegram_message(telegram_summary, bot_token, chat_id)
    else:
        # Just send a short notification
        notification = f"""
📚 *New Documentation Summary Available*

🔖 Repository: `{repo_name}`
📄 Full summary sent as document above

[View on GitHub](https://github.com/{repo_name})
"""
        msg_success = send_telegram_message(notification, bot_token, chat_id)
    
    return doc_success

def main():
    print("Starting Telegram summary task...")

    result = get_next_to_send()
    if result[0] is None:
        print("No summaries to send.")
        return

    summary_content, repo_name, queue_data = result

    print(f"Sending summary to Telegram for: {repo_name}")

    if send_summary_to_telegram(summary_content, repo_name):
        # Update queue
        sent_log = load_sent_log()
        sent_log[repo_name] = {
            "sent_at": datetime.now().isoformat(),
            "hash": get_summary_hash(summary_content)
        }
        save_sent_log(sent_log)

        queue_data["sent_order"].append(repo_name)
        queue_data["queue"].pop(0)
        save_queue(queue_data)

        print(f" Sent and logged: {repo_name}")
    else:
        print(f" Failed to send: {repo_name}")

if __name__ == "__main__":
    main()