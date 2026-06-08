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
# THM blocks API calls from bots; badge image is the only reliable source.
# Scrape the public profile page for stats instead.
lines += [
    "## TryHackMe · webstyr",
    "",
    f"[![TryHackMe](https://tryhackme-badges.s3.amazonaws.com/{THM_USER}.png)](https://tryhackme.com/p/{THM_USER})",
    "",
]

try:
    req = urllib.request.Request(
        f"https://tryhackme.com/p/{THM_USER}",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        page = r.read().decode("utf-8", errors="ignore")

    def scrape(pattern, text, default="N/A"):
        m = re.search(pattern, text)
        return html.unescape(m.group(1)).strip() if m else default

    rank   = scrape(r'"globalRank"\s*:\s*(\d+)', page)
    points = scrape(r'"points"\s*:\s*(\d+)', page)
    rooms  = scrape(r'"completedRooms"\s*:\s*(\d+)', page)
    badges = scrape(r'"totalBadges"\s*:\s*(\d+)', page)

    lines += [
        "| Metric | Value |",
        "|--------|-------|",
        f"| Global Rank | #{rank} |",
        f"| Points | {points} |",
        f"| Rooms Completed | {rooms} |",
        f"| Badges | {badges} |",
        "",
    ]
except Exception as e:
    print(f"Warning: THM scrape failed: {e}", file=sys.stderr)
    lines += [
        "| Metric | Value |",
        "|--------|-------|",
        "| Status | See badge above for live stats |",
        "",
    ]

# ── HackerOne (public GraphQL API) ─────────────────────────────────────────
lines += [
    "## HackerOne · webstyr",
    "",
    f"[![HackerOne](https://img.shields.io/badge/HackerOne-webstyr-ff6633?style=flat-square&logo=hackerone&logoColor=white)](https://hackerone.com/{H1_USER})",
    "",
]

try:
    query = json.dumps({
        "query": """
        {
          user(username: \"""" + H1_USER + """\") {
            reputation
            signal
            impact
            rank
            hackerProfile {
              bio
              website
            }
          }
        }
        """
    }).encode()

    req = urllib.request.Request(
        "https://hackerone.com/graphql",
        data=query,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.load(r)

    user = data.get("data", {}).get("user", {}) or {}
    reputation = user.get("reputation", "N/A")
    signal     = user.get("signal", "N/A")
    impact     = user.get("impact", "N/A")
    rank       = user.get("rank", "N/A")

    lines += [
        "| Metric | Value |",
        "|--------|-------|",
        f"| Reputation | {reputation} |",
        f"| Signal | {signal} |",
        f"| Impact | {impact} |",
        f"| Rank | #{rank} |",
        "",
    ]
except Exception as e:
    print(f"Warning: H1 GraphQL failed: {e}", file=sys.stderr)
    # fallback: scrape public profile page
    try:
        req = urllib.request.Request(
            f"https://hackerone.com/{H1_USER}",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            page = r.read().decode("utf-8", errors="ignore")

        def extract(pattern, text, default="N/A"):
            m = re.search(pattern, text)
            return html.unescape(m.group(1)).strip() if m else default

        reputation = extract(r'"reputation[_"]?\s*[":]+\s*(\d+)', page)
        signal     = extract(r'"signal[_"]?\s*[":]+\s*([\d.]+)', page)
        impact     = extract(r'"impact[_"]?\s*[":]+\s*([\d.]+)', page)
        rank       = extract(r'"rank[_"]?\s*[":]+\s*(\d+)', page)

        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Reputation | {reputation} |",
            f"| Signal | {signal} |",
            f"| Impact | {impact} |",
            f"| Rank | #{rank} |",
            "",
        ]
    except Exception as e2:
        print(f"Warning: H1 scrape also failed: {e2}", file=sys.stderr)
        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Profile | [hackerone.com/{H1_USER}](https://hackerone.com/{H1_USER}) |",
            "",
        ]

lines += [
    "---",
    f"*Sources: [TryHackMe](https://tryhackme.com/p/{THM_USER}) · [HackerOne](https://hackerone.com/{H1_USER})*",
]

with open("logs/platform-stats.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("Platform stats written successfully")
