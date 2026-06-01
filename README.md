# Daily Reinsurance Tech & AI Briefing

Sends a daily email briefing every weekday morning using Claude with live web search.

---

## Setup (one-time, ~15 minutes)

### Step 1 — Create a GitHub repository

1. Go to [github.com](https://github.com) and sign in (or create a free account)
2. Click **New repository** → name it `reinsurance-briefing` → **Create repository**
3. Upload these files into the repo (drag & drop works):
   - `scripts/generate_and_send.py`
   - `.github/workflows/daily-briefing.yml`

### Step 2 — Get your API keys

**Claude API key**
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Click **API Keys** → **Create Key** → copy it

**Gmail app password** (recommended sender — free, no extra account needed)
1. Go to your Google Account → **Security** → **2-Step Verification** (must be enabled)
2. Search for **App passwords** → create one named "Reinsurance Briefing"
3. Copy the 16-character password shown

> If you prefer a different email provider (Outlook, etc.), set `SMTP_HOST` and `SMTP_PORT`
> accordingly. Outlook: `smtp.office365.com` / `587`.

### Step 3 — Add secrets to GitHub

1. In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each of these:

| Secret name       | Value                                      |
|-------------------|--------------------------------------------|
| `ANTHROPIC_API_KEY` | Your Claude API key (starts with `sk-ant-`) |
| `EMAIL_TO`          | Your inbox address (where briefing arrives) |
| `EMAIL_FROM`        | The Gmail address you're sending FROM       |
| `EMAIL_PASSWORD`    | The 16-char Gmail app password              |
| `SMTP_HOST`         | `smtp.gmail.com` (or your provider's host)  |
| `SMTP_PORT`         | `587`                                       |

### Step 4 — Test it manually

1. Go to your repo → **Actions** tab
2. Click **Daily Reinsurance Briefing** → **Run workflow** → **Run workflow**
3. Watch the run — it takes ~2–3 minutes
4. Check your inbox ✉️

### Step 5 — You're done

The workflow runs automatically at **06:30 Zurich time, Monday–Friday**.

---

## Adjusting the schedule

Edit `.github/workflows/daily-briefing.yml` and change the cron line:

```yaml
- cron: '30 5 * * 1-5'   # 06:30 CEST (summer) weekdays
- cron: '30 4 * * 1-5'   # 06:30 CET  (winter) weekdays
- cron: '0 6 * * 1-5'    # 07:00 CEST weekdays
```

Cron is always UTC. Zurich is UTC+2 in summer (CEST), UTC+1 in winter (CET).

---

## Costs

- **GitHub Actions**: free (2,000 min/month on free tier; this uses ~3 min/day)
- **Claude API**: ~$0.10–0.30 per briefing depending on search results length
- **Gmail**: free

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Email not arriving | Check spam folder; verify `EMAIL_FROM` and `EMAIL_PASSWORD` secrets |
| `AuthenticationError` | Gmail app password must be used, not your regular password |
| `API key error` | Double-check `ANTHROPIC_API_KEY` secret — no extra spaces |
| Workflow not triggering | GitHub Actions cron can be delayed up to ~15 min |
