---
name: linkedin-post
description: Post content to LinkedIn via the Zernio API. Use when the user wants to create, schedule, or publish LinkedIn posts. Triggers on requests like "post to LinkedIn", "share on LinkedIn", "publish a LinkedIn post", "schedule a post", or any mention of posting content to LinkedIn.
---

# LinkedIn Posting via Zernio

Post content to LinkedIn using the Zernio API.

## First-Run Setup

**Every time this skill is invoked**, perform this exact check before doing anything else:

**Step 1 — Read the file.** Use the read_file tool to read `linkedin-post-config.md` from the workspace root.

**Step 2 — Check for all four fields** by scanning the file content for these exact patterns:
- `API Key:` followed by a non-empty value
- `Profile ID:` followed by a non-empty value
- `Account ID:` followed by a non-empty value
- `Timezone:` followed by a non-empty value

**Step 3 — Decide:**
- ✅ **All four fields found with values** → stop this section, proceed immediately to posting. Do NOT ask the user anything.
- ❌ **File missing OR any field is absent or empty** → collect only the missing fields (do not ask for fields that already exist):
  1. Tell the user: "I need a few details before posting — you'll only need to provide these once."
  2. Ask for each **missing** field only:
     - **API Key**: "What is your Zernio API key?" (Zernio dashboard → API settings)
     - **Profile ID**: "What is your Zernio Profile ID?" (Zernio dashboard → your profile)
     - **Account ID**: "What is your LinkedIn Account ID in Zernio?" (Zernio dashboard → Connected Accounts)
     - **Timezone**: "What city or country are you in? I'll use this to set your posting timezone."
       - Map to IANA timezone (e.g. "Toronto" / "Canada" → `America/Toronto`, "London" / "UK" → `Europe/London`, "Sydney" / "Australia" → `Australia/Sydney`, "Dubai" / "UAE" → `Asia/Dubai`)
  3. Write the complete file to the workspace root:

```
# LinkedIn Skill Configuration

## Credentials
- API Key: <value>
- Profile ID: <value>
- Timezone: <IANA timezone>

## LinkedIn Account (Personal Brand Profile)
- Account ID: <value>
```

  4. Confirm: "Config saved to `linkedin-post-config.md`. You won't be asked again unless you delete that file."

The script reads all values from this file at runtime. Override the config path with the `ZERNIO_CONFIG` environment variable if needed. If `Timezone` is absent, the script falls back to `UTC`.

## How to Post

**Endpoint:** `POST https://api.zernio.com/v1/posts`

**Headers:**
```
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

**Body:**
```json
{
  "profileId": "<profile_id from linkedin-post-config.md>",
  "platforms": [
    {
      "platform": "linkedin",
      "accountId": "<account_id from linkedin-post-config.md>"
    }
  ],
  "content": "<post content>",
  "scheduledFor": "<current ISO timestamp>",
  "timezone": "America/Toronto"
}
```

**⚠️ Important: Always use the file-based approach below.** Post content often contains emoji (❌✅🔐👇), parentheses, exclamation marks, and other characters that shells like zsh will misinterpret (glob expansion, history expansion, etc.). Passing JSON inline in a curl `-d` argument is unreliable.

**Correct method — use the helper script (handles emoji correctly):**

A helper script is available at `scripts/post-to-linkedin.py` in this skill directory.
It reads post content from a file, avoiding shell encoding issues with emoji and special characters.

```bash
# Step 1: Write post content to a file
cat > /tmp/linkedin-content.txt << 'POSTEOF'
Your post content here with emoji 🔐🚗
#Hashtags
POSTEOF

# Step 2: Post using the helper script
python3 $(find ~ -path "*/linkedin-post/scripts/post-to-linkedin.py" 2>/dev/null | head -1) /tmp/linkedin-content.txt
```

This bypasses all shell interpretation and emoji encoding issues entirely.

## Key Rules

- **Always include `scheduledFor`** with the current timestamp — this triggers immediate publishing via Zernio's pipeline.
- **Always include `timezone`** set to `America/Toronto`.
- Without `scheduledFor`, the post saves as a **draft** and will NOT publish.
- Do NOT set `status` manually — Zernio auto-publishes when `scheduledFor` is present.
- On success, the response includes `platformPostUrl` — the live LinkedIn post URL.

## Verify Connection

To check if LinkedIn is still connected:

```bash
curl -s "https://api.zernio.com/v1/accounts" \
  -H "Authorization: Bearer <API_KEY>"
```

Look for `platformStatus: "active"` and `isActive: true` in the response.
