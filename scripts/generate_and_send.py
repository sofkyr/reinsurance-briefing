#!/usr/bin/env python3
"""
Daily Reinsurance Tech & AI Briefing
Calls Claude API with web search, then emails the result.
"""

import os
import json
import smtplib
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.error

# ── Config (all from environment variables / GitHub Secrets) ──────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
EMAIL_TO          = os.environ["EMAIL_TO"]           # your inbox
EMAIL_FROM        = os.environ["EMAIL_FROM"]          # sender address
EMAIL_PASSWORD    = os.environ["EMAIL_PASSWORD"]      # Gmail app password or SMTP password
SMTP_HOST         = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT         = int(os.environ.get("SMTP_PORT", "587"))

TODAY = datetime.now().strftime("%B %d, %Y")
WEEKDAY = datetime.now().strftime("%A")

# ── Prompt ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are briefing a Chief Technology, Data & AI Officer at a reinsurance company (SCOR).
They want to stay current on tech, data and AI moves across incumbents, peers, and emerging players —
including thought leadership from major consultancies.

## Scope — STRICT
Only include stories about: AI, machine learning, data platforms, analytics, technology strategy,
digital underwriting, InsurTech, cyber tech, or data/tech partnerships.

Exclude entirely: financial results, renewals pricing, people moves, M&A (unless tech-driven),
cat losses, capital markets, general strategy. If a story has no meaningful tech/data/AI angle, skip it.

Freshness: only include items published within the last 7 days. If the publication date is unclear, skip it.

## Output Format
Bold headline, one punchy clause (max 15 words), link. No news = skip section entirely.

Structure (use markdown):

📅 [DATE] — Reinsurance Tech & AI Briefing

🏢 INCUMBENTS & LARGE CARRIERS
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🔄 REINSURANCE PEERS
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🚀 EMERGING / INSURTECH
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🇬🇧 LONDON MARKET (KI, Beazley, Convex, Conduit, and other Lloyd's/London players)
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🤖 AI & DATA IN (RE)INSURANCE
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🎓 CONSULTING & THOUGHT LEADERSHIP (McKinsey, Bain, BCG)
- **[Headline]** — [One clause, max 15 words.] [Source](url)

🏦 FINANCIAL SERVICES (JP Morgan, Goldman Sachs, UBS, and other major FS players)
- **[Headline]** — [One clause, max 15 words.] [Source](url)

💬 AI THOUGHT LEADERS (Sam Altman, Dario Amodei, Demis Hassabis, Yann LeCun, and other prominent AI voices)
- **[Headline / Quote]** — [One clause, max 15 words.] [Source](url)

Rules:
- Skip any section with no qualifying news — no apology needed
- Max ~5 bullets per section
- Links must be real and verified from search results
- If nothing qualifies across all sections: "No significant tech, data or AI developments in the last 7 days."
"""

USER_PROMPT = f"""Today is {TODAY} ({WEEKDAY}). Please produce the daily Reinsurance Tech & AI Briefing.

Run web searches using today's date. Use these searches:
1. Munich Re Swiss Re Hannover Re SCOR AI data technology {datetime.now().strftime('%B %Y')}
2. AXA XL Allianz Zurich insurance AI data platform {datetime.now().strftime('%B %Y')}
3. insurtech AI data machine learning funding launch {datetime.now().strftime('%B %Y')}
4. KI Insurance Beazley Convex Conduit Lloyd's AI data digital {datetime.now().strftime('%B %Y')}
5. reinsurance insurance AI underwriting data analytics tool {datetime.now().strftime('%B %Y')}
6. McKinsey Bain BCG insurance reinsurance AI data technology {datetime.now().strftime('%B %Y')}
7. JP Morgan Goldman Sachs UBS AI data technology strategy {datetime.now().strftime('%B %Y')}
8. Sam Altman Dario Amodei AI interview quote Forbes Fortune {datetime.now().strftime('%B %Y')}

Prioritize sources: The Insurer, Reinsurance News, Insurance Insider, Artemis, Business Wire,
press releases, company newsrooms, mckinsey.com, bain.com, bcg.com, Fortune, Forbes, Bloomberg, FT, WSJ.

Only include items published within the last 7 days.
"""

# ── Call Claude API with web search ──────────────────────────────────────────
def call_claude() -> str:
    payload = {
        "model": "claude-opus-4-5",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "tools": [
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10
            }
        ],
        "messages": [
            {"role": "user", "content": USER_PROMPT}
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "interleaved-thinking-2025-05-14",
            "content-type": "application/json",
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    # Extract all text blocks from the response
    text_parts = [
        block["text"]
        for block in result.get("content", [])
        if block.get("type") == "text"
    ]
    return "\n".join(text_parts)


# ── Convert markdown to basic HTML for email ─────────────────────────────────
def markdown_to_html(md: str) -> str:
    lines = md.split("\n")
    html_lines = []
    for line in lines:
        # Headers / emoji section titles
        if line.startswith("📅"):
            line = f"<h2 style='color:#1a1a2e;border-bottom:2px solid #e8e8f0;padding-bottom:8px'>{line}</h2>"
        elif any(line.startswith(e) for e in ["🏢","🔄","🚀","🇬🇧","🤖","🎓","🏦","💬"]):
            line = f"<h3 style='color:#2c3e6b;margin-top:24px;margin-bottom:8px'>{line}</h3>"
        # Bullet points
        elif line.startswith("- "):
            inner = line[2:]
            # Bold **text**
            inner = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', inner)
            # Links [text](url)
            inner = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#4a6fa5">\1</a>', inner)
            line = f"<li style='margin:6px 0;line-height:1.5'>{inner}</li>"
        else:
            # Inline bold and links in regular lines
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#4a6fa5">\1</a>', line)
            if line.strip():
                line = f"<p style='margin:4px 0'>{line}</p>"
        html_lines.append(line)

    body = "\n".join(html_lines)
    return f"""
    <html><body style='font-family:Georgia,serif;max-width:680px;margin:auto;
    padding:32px 24px;color:#1a1a1a;background:#fafafa;line-height:1.6'>
    <div style='background:white;padding:32px;border-radius:8px;
    box-shadow:0 1px 4px rgba(0,0,0,0.08)'>
    {body}
    <hr style='margin-top:32px;border:none;border-top:1px solid #e8e8f0'>
    <p style='font-size:12px;color:#888;margin-top:12px'>
    Generated by Claude · Reinsurance Tech & AI Briefing · {TODAY}
    </p>
    </div></body></html>
    """


# ── Send email ────────────────────────────────────────────────────────────────
def send_email(briefing_md: str):
    subject = f"☀️ Reinsurance Tech & AI Briefing — {TODAY}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO

    # Plain text fallback
    msg.attach(MIMEText(briefing_md, "plain"))
    # HTML version
    msg.attach(MIMEText(markdown_to_html(briefing_md), "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print(f"✅ Briefing sent to {EMAIL_TO}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🔍 Generating briefing for {TODAY}...")
    briefing = call_claude()
    print("📧 Sending email...")
    send_email(briefing)
    print("Done.")
