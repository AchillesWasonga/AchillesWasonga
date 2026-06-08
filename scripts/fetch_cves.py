import json, sys, urllib.request
from datetime import datetime, timezone

date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
time = datetime.now(timezone.utc).strftime("%H:%M UTC")

try:
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?cvssV3Severity=CRITICAL&resultsPerPage=10&startIndex=0"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
except Exception as e:
    data = {}
    print(f"Warning: could not fetch NVD data: {e}", file=sys.stderr)

vulns = data.get("vulnerabilities", [])

lines = [
    f"# CVE Feed — {date}",
    "",
    f"> Auto-fetched daily from NVD · Last updated: {time}",
    "",
    "| CVE ID | Description | CVSS Score | Published |",
    "|--------|-------------|------------|-----------|",
]

for v in vulns:
    cve       = v.get("cve", {})
    cve_id    = cve.get("id", "N/A")
    published = cve.get("published", "")[:10]
    descs     = cve.get("descriptions", [])
    desc      = next((d["value"] for d in descs if d["lang"] == "en"), "No description")
    desc      = (desc[:120] + "...") if len(desc) > 120 else desc
    desc      = desc.replace("|", "/").replace("\n", " ")
    metrics   = cve.get("metrics", {})
    score     = "N/A"
    for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
        if key in metrics and metrics[key]:
            score = metrics[key][0].get("cvssData", {}).get("baseScore", "N/A")
            break
    lines.append(f"| [{cve_id}](https://nvd.nist.gov/vuln/detail/{cve_id}) | {desc} | {score} | {published} |")

if not vulns:
    lines.append("| — | No data returned from NVD | — | — |")

lines += ["", "---", "*Sources: [NVD](https://nvd.nist.gov/) · [CVE.org](https://www.cve.org/)*"]

with open("logs/cve-feed.md", "w") as f:
    f.write("\n".join(lines) + "\n")

print("CVE feed written successfully")
