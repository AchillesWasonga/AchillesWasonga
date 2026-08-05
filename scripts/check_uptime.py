"""Check the monitored sites and write logs/uptime.md.

A monitor must never fail because the thing it monitors failed, so every
network error is caught and recorded as a status rather than raised.
"""

import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITES = [
    ("wasonga.com",         "https://wasonga.com"),
    ("campdevoices.org",    "https://campdevoices.org"),
    ("motorsportsplug.com", "https://www.motorsportsplug.com/"),
    ("kimtailangat.com",    "https://www.kimtailangat.com/"),
    ("elitetechafrica.org", "https://www.elitetechafrica.org/"),
]

TIMEOUT = 15
HISTORY_ROWS = 30
LOG = Path("logs/uptime.md")
HISTORY = Path("logs/uptime-history.md")

date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
time_str = datetime.now(timezone.utc).strftime("%H:%M UTC")


def check(url):
    """Return (status, http_code, latency_ms). Never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": "webstyr-uptime-bot/1.0"})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code  # the server answered, it just wasn't a success
    except urllib.error.URLError as e:
        ms = round((time.monotonic() - start) * 1000)
        # No DNS record is a different failure from a host that refuses us.
        status = "NO_DNS" if isinstance(e.reason, socket.gaierror) else "DOWN"
        return status, "—", ms
    except Exception:
        ms = round((time.monotonic() - start) * 1000)
        return "DOWN", "—", ms

    ms = round((time.monotonic() - start) * 1000)
    return ("UP" if 200 <= code < 400 else "DOWN"), str(code), ms


results = [(name, url, *check(url)) for name, url in SITES]

# ── History: one row per day, newest last. Re-runs replace the day's row. ──
HISTORY.parent.mkdir(parents=True, exist_ok=True)
old = HISTORY.read_text().splitlines() if HISTORY.exists() else []
old = [r for r in old if r.strip() and not r.startswith(f"| {date} ")]
row = f"| {date} | " + " | ".join(status for _, _, status, _, _ in results) + " |"
HISTORY.write_text("\n".join(old + [row]) + "\n")

lines = [
    f"# Uptime Monitor — {date}",
    "",
    f"> Auto-checked daily · Last updated: {time_str}",
    "",
    "| Site | Status | HTTP | Latency |",
    "|------|--------|------|---------|",
]
for name, url, status, code, ms in results:
    lines.append(f"| [{name}]({url}) | {status} | {code} | {ms}ms |")

lines += [
    "",
    "## History",
    "",
    "| Date | " + " | ".join(name for name, _ in SITES) + " |",
    "|------|" + "|".join("-" * (len(name) + 2) for name, _ in SITES) + "|",
]
lines += (old + [row])[-HISTORY_ROWS:]

lines += [
    "",
    "---",
    "*Monitored by webstyr-bot · checks run daily at 10:00 UTC*",
]

LOG.write_text("\n".join(lines) + "\n")

for name, _, status, code, ms in results:
    print(f"{name}: {status} ({code}) {ms}ms")
print("Uptime log written successfully")
