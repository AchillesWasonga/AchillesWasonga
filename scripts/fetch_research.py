import urllib.request, json, xml.etree.ElementTree as ET, sys
from datetime import datetime, timezone

date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
time = datetime.now(timezone.utc).strftime("%H:%M UTC")

SECURITY_TERMS = [
    "exploit", "vulnerability", "cve", "hack", "malware", "ransomware",
    "phishing", "zero-day", "0day", "pentest", "injection", "xss", "sql",
    "rce", "llm", "ai security", "reverse engineer", "cryptography",
    "encryption", "breach", "threat", "attack", "shellcode", "privilege",
    "escalation", "lateral movement", "red team", "blue team", "osint",
    "recon", "bug bounty", "ctf", "capture the flag",
]

lines = [
    f"# Security Research — {date}",
    "",
    f"> Auto-fetched daily from Hacker News and arXiv · Last updated: {time}",
    "",
    "## Hacker News · Security & Hacking",
    "",
    "| Title | Points | Comments |",
    "|-------|--------|----------|",
]

try:
    with urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=15) as r:
        story_ids = json.load(r)[:100]

    stories = []
    for sid in story_ids:
        try:
            with urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10) as r:
                s = json.load(r)
            title = s.get("title", "")
            if any(t in title.lower() for t in SECURITY_TERMS):
                stories.append(s)
            if len(stories) >= 8:
                break
        except Exception:
            continue

    if stories:
        for s in stories:
            title    = s.get("title", "N/A").replace("|", "/")
            url      = s.get("url", f"https://news.ycombinator.com/item?id={s.get('id')}")
            points   = s.get("score", 0)
            comments = s.get("descendants", 0)
            lines.append(f"| [{title}]({url}) | {points} | {comments} |")
    else:
        lines.append("| No security stories in top 100 today | — | — |")
except Exception as e:
    lines.append(f"| Error fetching HN: {e} | — | — |")
    print(f"Warning: HN fetch failed: {e}", file=sys.stderr)

NS = "http://www.w3.org/2005/Atom"

lines += [
    "",
    "## arXiv · Latest Papers (cs.CR + cs.AI)",
    "",
    "| Title | Authors | Published |",
    "|-------|---------|-----------|",
]

entries = []
for cat in ["cs.CR", "cs.AI"]:
    try:
        url = f"https://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results=4"
        with urllib.request.urlopen(url, timeout=20) as r:
            tree = ET.parse(r)
        for entry in tree.findall(f"{{{NS}}}entry"):
            title     = (entry.findtext(f"{{{NS}}}title") or "").replace("\n", " ").strip()
            link      = (entry.findtext(f"{{{NS}}}id") or "").strip()
            published = (entry.findtext(f"{{{NS}}}published") or "")[:10]
            authors   = [a.findtext(f"{{{NS}}}name") for a in entry.findall(f"{{{NS}}}author")]
            author_str = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
            entries.append((title, link, author_str, published))
    except Exception as e:
        print(f"Warning: arXiv {cat} fetch failed: {e}", file=sys.stderr)

if entries:
    for title, link, authors, published in entries[:8]:
        t = title.replace("|", "/")
        a = authors.replace("|", "/")
        lines.append(f"| [{t}]({link}) | {a} | {published} |")
else:
    lines.append("| Could not fetch arXiv papers | — | — |")

lines += ["", "---", "*Sources: [Hacker News](https://news.ycombinator.com) · [arXiv cs.CR](https://arxiv.org/list/cs.CR/recent) · [arXiv cs.AI](https://arxiv.org/list/cs.AI/recent)*"]

with open("logs/research.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("Research digest written successfully")
