# 📚 GitHub Docs Summarizer

> Automatically fetch, summarize, and email documentation from your starred GitHub repositories using OpenAI. Get daily AI-generated summaries of your favorite projects delivered to your inbox.

![Python](https://img.shields.io/badge/python-3.11-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-green)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## Features

-  **Auto-fetch** documentation from your starred GitHub repositories
-  **AI-powered summaries** using OpenAI GPT-4o-mini
-  **Daily email delivery** of one summary per day
-  **Cyclic sending** - once all summaries are sent, restarts from beginning
-  **Auto-detects new repos** - new starred repos are automatically included
-  **Fully automated** via GitHub Actions - zero manual work after setup

---

## How It Works

```
Every Sunday 2 AM UTC (Can be modified)
    ↓
Fetch all starred GitHub repos
    ↓
Clone repos → Extract docs → Generate AI summary
    ↓
Push summaries to repository
    ↓
Every Day 9 AM UTC (Can be modified)
    ↓
Send one summary via email
    ↓
Track sent summaries (cyclic)
```

---
## 📹 Quick Demo

https://github.com/user-attachments/assets/bbda97b8-9f80-4671-98fd-faf8ed4bcdee

---
## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- GitHub Personal Access Token
- Gmail account with App Password enabled

---

## Setup Guide

### Step 1: Fork & Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/github-docs-summarizer.git
cd github-docs-summarizer
```

### Step 2: Install uv

```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 3: Install Dependencies

```bash
uv add openai requests python-dotenv
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Fill in your values:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxx

# GitHub
GIT_TOKEN=ghp_xxxxxxxxxxxxxx

# Email (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_API=xxxx xxxx xxxx xxxx
GMAIL_USER=your-email@gmail.com
RECIPIENT_EMAIL=recipient@gmail.com
```

### Step 5: Configure GitHub Secrets

Go to your forked repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets (paste values without quotes):

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `OPENAI_API_KEY` | `sk-proj-xxx...` | [OpenAI API Keys](https://platform.openai.com/api-keys) |
| `GIT_TOKEN` | `ghp_xxx...` | [GitHub Tokens](https://github.com/settings/tokens) |
| `SMTP_HOST` | `smtp.gmail.com` | Fixed value |
| `SMTP_PORT` | `587` | Fixed value |
| `SMTP_API` | `xxxx xxxx xxxx xxxx` | [Gmail App Password](https://myaccount.google.com/apppasswords) |
| `GMAIL_USER` | `your-email@gmail.com` | Your Gmail address |
| `RECIPIENT_EMAIL` | `recipient@gmail.com` | Where to send summaries |

#### How to get each credential:

<details>
<summary>🔑 OpenAI API Key</summary>

1. Go to https://platform.openai.com/api-keys
2. Click **Create new secret key**
3. Give it a name (e.g., `github-docs-summarizer`)
4. Copy the key (starts with `sk-proj-`)
</details>

<details>
<summary>🔑 GitHub Personal Access Token</summary>

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Give it a name (e.g., `github-docs-summarizer`)
4. Select scope: ✅ `repo`
5. Click **Generate token**
6. Copy the token (starts with `ghp_`)
</details>

<details>
<summary>🔑 Gmail App Password</summary>

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** (required)
3. Go to https://myaccount.google.com/apppasswords
4. Select **Mail** and **Windows Computer**
5. Click **Generate**
6. Copy the 16-character password (e.g., `xxxx xxxx xxxx xxxx`)
</details>

---

### Step 6: Test Locally

```bash
uv run test_mail.py
uv run client.py
uv run mail.py
```

### Step 7: Enable GitHub Actions

1. Go to your forked repository
2. Click **Actions** tab
3. Click **I understand my workflows, go ahead and enable them**

That's it! 🎉 The workflows will run automatically.

---

## Configuration

### Change Email Schedule

Edit `.github/workflows/daily-email.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize the schedule.

| Schedule | Cron |
|----------|------|
| Every day at 9 AM UTC | `0 9 * * *` |
| Every day at 6 PM UTC | `0 18 * * *` |
| Every Monday at 9 AM UTC | `0 9 * * 1` |

### Change Summary Generation Schedule

Edit `.github/workflows/weekly-generate.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * 0'
```

### Manually Trigger Workflows

Go to **Actions** tab → Select workflow → Click **Run workflow**
---

## Email Tracking

The system tracks sent summaries in `sent_summaries.json`:

```json
{
  "sent": [
    "owner1_repo1",
    "owner2_repo2"
  ],
  "timestamp": {
    "owner1_repo1": "2026-02-21T09:00:00",
    "owner2_repo2": "2026-02-22T09:00:00"
  }
}
```

- Once all summaries are sent, **cycle restarts automatically**
- New starred repos are **automatically included** in the next cycle

---

## 🔄 Workflow

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| `weekly-generate.yml` | Every Sunday 2 AM UTC | Fetches starred repos, generates summaries, pushes to git |
| `daily-email.yml` | Every day 9 AM UTC | Sends one summary email, tracks sent status |

---

## Troubleshooting

<details>
<summary>Email not sending</summary>

- Check `GMAIL_USER` and `SMTP_API` secrets are correct
- Make sure 2-Step Verification is enabled on Gmail
- Generate a new App Password if needed
- Run `uv run test_mail.py` to test locally
</details>

<details>
<summary>No summaries generated</summary>

- Check `GIT_TOKEN` has `repo` scope
- Check `OPENAI_API_KEY` is valid
- Make sure you have starred repositories on GitHub
- Run `uv run client.py` locally to debug
</details>

<details>
<summary>Rate limit errors (429)</summary>

- OpenAI rate limits depend on your plan
- The system has automatic retry with exponential backoff
- Consider upgrading your OpenAI plan for faster processing
- Reduce `max_chars` in `client.py` if needed
</details>

<details>
<summary>Workflow not running</summary>

- Make sure GitHub Actions is enabled in your fork
- Check **Actions** tab for error logs
- Verify all secrets are configured correctly
- Try manually triggering the workflow
</details>

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">Made with ❤️ | Give it a ⭐ if you find it useful!</p>