import urllib.request, json, re, html, sys
from datetime import datetime, timezone

date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
time = datetime.now(timezone.utc).strftime("%H:%M UTC")

THM_USER = "webstyr"
H1_USER  = "webstyr"

lines = [
    f"# Platform Stats — {date}",
    "",
    f"> Auto-fetched daily · Last updated: {time}",
    "",
]

# ── TryHackMe ──────────────────────────────────────────────────────────────
lines += ["## TryHackMe · webstyr", "", f"[![TryHackMe](https://tryhackme-badges.s3.amazonaws.com/{THM_USER}.png)](https://tryhackme.com/p/{THM_USER})", ""]

def thm_fetch(path):
    try:
        req = urllib.request.Request(
            f"https://tryhackme.com{path}",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        print(f"Warning: THM fetch {path} failed: {e}", file=sys.stderr)
        return None

rank_data   = thm_fetch(f"/api/user/rank/{THM_USER}")
badges_data = thm_fetch(f"/api/user/badges/{THM_USER}")

lines += ["| Metric | Value |", "|--------|-------|"]
if rank_data:
    lines += [
        f"| Global Rank | #{rank_data.get('globalRank', 'N/A')} |",
        f"| Points | {rank_data.get('points', 'N/A')} |",
        f"| Rooms Completed | {rank_data.get('completedRooms', 'N/A')} |",
        f"| Country Rank | #{rank_data.get('countryRank', 'N/A')} |",
    ]
else:
    lines.append("| Status | Profile fetched via badge |")

badge_count = len(badges_data) if isinstance(badges_data, list) else "N/A"
lines.append(f"| Badges | {badge_count} |")
lines.append("")

# ── HackerOne ──────────────────────────────────────────────────────────────
lines += [
    "## HackerOne · webstyr",
    "",
    f"[![HackerOne](https://img.shields.io/badge/HackerOne-webstyr-ff6633?style=flat-square&logo=hackerone&logoColor=white)](https://hackerone.com/{H1_USER})",
    "",
]

try:
    req = urllib.request.Request(
        f"https://hackerone.com/{H1_USER}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        page = r.read().decode("utf-8", errors="ignore")
except Exception as e:
    page = ""
    print(f"Warning: H1 scrape failed: {e}", file=sys.stderr)

def extract(pattern, text, default="N/A"):
    m = re.search(pattern, text)
    return html.unescape(m.group(1)).strip() if m else default

reputation = extract(r'"reputation"[:\s]+(\d+)', page)
signal     = extract(r'"signal"[:\s]+([\d.]+)', page)
impact     = extract(r'"impact"[:\s]+([\d.]+)', page)
rank       = extract(r'"rank"[:\s]+(\d+)', page)

lines += [
    "| Metric | Value |",
    "|--------|-------|",
    f"| Reputation | {reputation} |",
    f"| Signal | {signal} |",
    f"| Impact | {impact} |",
    f"| Rank | #{rank} |",
    "",
    "---",
    f"*Sources: [TryHackMe](https://tryhackme.com/p/{THM_USER}) · [HackerOne](https://hackerone.com/{H1_USER})*",
]

with open("logs/platform-stats.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("Platform stats written successfully")
