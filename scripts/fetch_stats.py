import urllib.request, json, sys
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
# Every tryhackme.com page and API sits behind a Vercel bot checkpoint, so
# scraping always fails. The badge image is served from S3 and stays live.
lines += [
    "## TryHackMe · webstyr",
    "",
    f"[![TryHackMe](https://tryhackme-badges.s3.amazonaws.com/{THM_USER}.png)](https://tryhackme.com/p/{THM_USER})",
    "",
    "*Live rank, points and badges are shown on the badge above.*",
    "",
]

# ── HackerOne (public GraphQL API) ─────────────────────────────────────────
# The API answers for any public profile, but returns null stats until the
# account has reputation, so only show the table when there's real data.
lines += [
    "## HackerOne · webstyr",
    "",
    f"[![HackerOne](https://img.shields.io/badge/HackerOne-webstyr-ff6633?style=flat-square&logo=hackerone&logoColor=white)](https://hackerone.com/{H1_USER})",
    "",
]

user = {}
try:
    query = json.dumps({
        "query": "query($u: String!) { user(username: $u) { reputation signal impact rank } }",
        "variables": {"u": H1_USER},
    }).encode()
    req = urllib.request.Request(
        "https://hackerone.com/graphql",
        data=query,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        user = (json.load(r).get("data") or {}).get("user") or {}
except Exception as e:
    print(f"Warning: H1 GraphQL failed: {e}", file=sys.stderr)

stats = [
    ("Reputation", user.get("reputation"), ""),
    ("Signal",     user.get("signal"),     ""),
    ("Impact",     user.get("impact"),     ""),
    ("Rank",       user.get("rank"),       "#"),
]
if any(value is not None for _, value, _ in stats):
    lines += ["| Metric | Value |", "|--------|-------|"]
    for label, value, prefix in stats:
        lines.append(f"| {label} | {prefix}{value} |" if value is not None else f"| {label} | — |")
    lines.append("")
else:
    lines += [
        f"*No public stats yet — see [hackerone.com/{H1_USER}](https://hackerone.com/{H1_USER}).*",
        "",
    ]

lines += [
    "---",
    f"*Sources: [TryHackMe](https://tryhackme.com/p/{THM_USER}) · [HackerOne](https://hackerone.com/{H1_USER})*",
]

with open("logs/platform-stats.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("Platform stats written successfully")
