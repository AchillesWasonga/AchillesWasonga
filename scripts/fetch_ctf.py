import json, sys, random, urllib.request
from datetime import datetime, timezone

date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
time = datetime.now(timezone.utc).strftime("%H:%M UTC")

try:
    now = int(datetime.now(timezone.utc).timestamp())
    url = f"https://ctftime.org/api/v1/events/?limit=10&start={now}"
    req = urllib.request.Request(url, headers={"User-Agent": "webstyr-ctf-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        events = json.load(r)
except Exception as e:
    events = []
    print(f"Warning: could not fetch CTFtime: {e}", file=sys.stderr)

FALLBACK = [
    ("Pwn College",          "https://pwn.college",                          "Binary exploitation and system security",           "pwn/re"),
    ("PicoCTF",              "https://picoctf.org",                          "Beginner-friendly challenges across all categories", "misc"),
    ("HackTheBox",           "https://hackthebox.com",                       "Real-world penetration testing labs",                "web/pwn/re"),
    ("OverTheWire: Bandit",  "https://overthewire.org/wargames/bandit/",    "Linux fundamentals via wargame",                    "linux"),
    ("CryptoHack",           "https://cryptohack.org",                       "Cryptography challenges",                           "crypto"),
]

lines = [
    "# CTF Challenge of the Day",
    "",
    f"> Auto-fetched daily from CTFtime · Last updated: {time}",
    "",
]

if events:
    e        = random.choice(events[:10]) if len(events) >= 10 else events[0]
    title    = e.get("title", "Unknown CTF")
    url      = e.get("url", e.get("ctftime_url", "#"))
    desc     = e.get("description", "No description available.")
    desc     = (desc[:300] + "...") if len(desc) > 300 else desc
    fmt      = e.get("format", "Unknown")
    weight   = e.get("weight", "N/A")
    start    = e.get("start", "")[:10]
    finish   = e.get("finish", "")[:10]
    orgs     = e.get("organizers", [{}])
    org_name = orgs[0].get("name", "Unknown") if orgs else "Unknown"

    lines += [
        f"## [{title}]({url})",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Format | {fmt} |",
        f"| Weight | {weight} |",
        f"| Organizer | {org_name} |",
        f"| Start | {start} |",
        f"| End | {finish} |",
        "",
        "### Description",
        "",
        desc,
        "",
    ]
else:
    c = random.choice(FALLBACK)
    lines += [
        f"## [{c[0]}]({c[1]})",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Category | {c[3]} |",
        "",
        "### Description",
        "",
        c[2],
        "",
    ]

lines += ["---", "*Sources: [CTFtime](https://ctftime.org) · [PicoCTF](https://picoctf.org) · [HackTheBox](https://hackthebox.com)*"]

with open("logs/ctf-challenge.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("CTF challenge written successfully")
