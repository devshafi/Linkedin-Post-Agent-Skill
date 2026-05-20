# linkedin-post

> Post to LinkedIn directly from Claude Code or OpenClaw — no browser needed.

![Claude Code](https://img.shields.io/badge/Claude%20Code-tested-blue)
![OpenClaw](https://img.shields.io/badge/OpenClaw-tested-purple)
![Python](https://img.shields.io/badge/Python-3.x-green)
![Zernio API](https://img.shields.io/badge/API-Zernio-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## What This Skill Does

`linkedin-post` is a Claude skill that lets your AI agent publish posts to LinkedIn on your behalf — directly from the terminal, without opening a browser or logging in manually.

It works by connecting to the [Zernio](https://zernio.com) API, which handles the LinkedIn OAuth layer for you. Once configured, you simply tell Claude what to post and it handles the rest: encoding, API call, and confirmation.

**What it handles automatically:**
- One-time credential setup (asks once, saves forever)
- Emoji and special character encoding (no shell interpretation issues)
- Immediate publishing (not drafts) via the `scheduledFor` mechanism
- Returns the live LinkedIn post URL on success

**What it does NOT do:**
- It does not require browser login after initial Zernio OAuth setup
- It does not store session cookies or tokens — only your Zernio API key

---

## How It Works

```
You tell Claude → Skill reads config → Python script called → Zernio API → LinkedIn post published
```

The post content is written to a temporary file before being sent, which avoids shell encoding bugs with emoji and special characters (a common failure point when passing JSON inline in curl).

---

## First-Time Setup

### Prerequisites

- Python 3 (standard library only — no `pip install` needed)
- A [Zernio](https://zernio.com) account with your LinkedIn account connected
- Claude Code CLI **or** OpenClaw

### Steps

1. **Install the skill** by placing this folder in your Claude Code / OpenClaw skills directory.

2. **Trigger it** with any LinkedIn post request, for example:
   ```
   Post this to LinkedIn: "Excited to share my latest project..."
   ```

3. **On first run**, the skill detects the missing config and asks for four values (once only):
   - **Zernio API Key** — from Zernio dashboard → API settings
   - **Profile ID** — from Zernio dashboard → your profile
   - **Account ID** — from Zernio dashboard → Connected Accounts
   - **Timezone** — your city or country (e.g. "Dhaka", "London", "Toronto")

4. The config is saved to `linkedin-post-config.md` at your workspace root:
   ```markdown
   # LinkedIn Skill Configuration

   ## Credentials
   - API Key: sk_xxxxxxxxxxxxxxxxxxxxx
   - Profile ID: <your_profile_id>
   - Timezone: Asia/Dhaka

   ## LinkedIn Account (Personal Brand Profile)
   - Account ID: <your_account_id>
   ```

5. Every subsequent post works immediately — no prompts.

---

## Usage Examples

Just speak naturally to Claude:

```
Post this to LinkedIn: "Just shipped a new feature..."
```

```
Share this on LinkedIn: [paste your content]
```

```
Publish a LinkedIn post about the importance of agentic AI workflows.
```

```
Schedule a post to LinkedIn: "Reflecting on this week's learnings..."
```

The skill activates on keywords like: *post to LinkedIn*, *share on LinkedIn*, *publish a LinkedIn post*, *schedule a post*.

---

## Tested With

- **Claude Code** (CLI) — invoke via `/linkedin-post` or natural language triggers
- **OpenClaw** — works the same way; benefits from additional automation features (see below)

---

## Advanced: Scheduling & Notifications via OpenClaw

If you use [OpenClaw](https://openclaw.ai), you can go further:

- **Cron-based scheduling** — set up recurring LinkedIn posts on a fixed schedule (e.g. every Monday morning) using OpenClaw's built-in cron job support
- **Telegram notifications** — get notified via your Telegram channel when a post is successfully published, so you always know when something went live

These features are configured at the OpenClaw level and do not require changes to this skill.

---

## Verifying Your LinkedIn Connection

To check that your LinkedIn account is still connected in Zernio:

```bash
curl -s "https://api.zernio.com/v1/accounts" \
  -H "Authorization: Bearer <YOUR_API_KEY>"
```

Look for `"platformStatus": "active"` and `"isActive": true` in the response. If not, re-authorize in the Zernio dashboard.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Post saved as draft, not published | `scheduledFor` missing | Use the provided script — it sets this automatically |
| Emoji missing or garbled | Inline JSON passed via shell | Always use `scripts/post-to-linkedin.py`, not raw curl |
| LinkedIn disconnected error | OAuth token expired in Zernio | Re-connect LinkedIn in the Zernio dashboard |
| Config fields not found | Config file format changed | Re-check `linkedin-post-config.md` matches the format above |

---

## ⚠️ API Key Security Warning

`linkedin-post-config.md` stores your Zernio API key in **plain text**. Before pushing this project to GitHub:

- **Add the config file to `.gitignore`** immediately:
  ```
  linkedin-post-config.md
  ```
- Anyone with your API key can post to your LinkedIn account
- If the key is ever exposed, rotate it immediately from the Zernio dashboard → API settings
- To store the config outside your project directory, set the `ZERNIO_CONFIG` environment variable to an absolute path:
  ```bash
  export ZERNIO_CONFIG=/home/yourname/.secrets/linkedin-post-config.md
  ```

---

## File Structure

```
linkedin-post/
├── SKILL.md                  # Skill definition (read by Claude / OpenClaw)
├── scripts/
│   └── post-to-linkedin.py   # Python helper — handles encoding + API call
└── README.md                 # This file
```

The `linkedin-post-config.md` config file lives at your **workspace root** (not inside this skill folder) and is created automatically on first run.

---

## Requirements

- Python 3.x (no external packages — uses standard library only)
- A [Zernio](https://zernio.com) account with LinkedIn OAuth connected
- Claude Code CLI or OpenClaw

---

## License

MIT — see [LICENSE](LICENSE) for details.
