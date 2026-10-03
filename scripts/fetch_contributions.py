import sys
import json
import re
import ssl
from pathlib import Path
from datetime import datetime

# Import requests independently of bs4
try:
    import requests
except ImportError:
    requests = None

# BeautifulSoup optional for HTML parsing
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# SSL context for urllib fallback using certifi if available
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

import urllib.request

USERNAME = "Karmansingh09"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if requests is not None:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    else:
        req = urllib.request.Request(URL, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as resp:
            return resp.read().decode("utf-8")


def parse_contributions(html):
    days = []

    # BeautifulSoup parser if available
    if BeautifulSoup is not None:
        soup = BeautifulSoup(html, "html.parser")
        tooltips = soup.find_all(["tool-tip", "div"], attrs={"for": True})
        tip_dict = {}
        for tip in tooltips:
            for_id = tip.get("for")
            text = tip.get_text(strip=True)
            tip_dict[for_id] = text

        tds = soup.find_all("td", class_="ContributionCalendar-day")
        for td in tds:
            d_date = td.get("data-date")
            if not d_date:
                continue
            level = int(td.get("data-level", 0))
            elem_id = td.get("id")
            count = 0
            if elem_id and elem_id in tip_dict:
                tip_text = tip_dict[elem_id]
                m = re.search(r"(\d+)\s+contribution", tip_text)
                if m:
                    count = int(m.group(1))
                elif "No contribution" in tip_text or "0 contribution" in tip_text:
                    count = 0
                else:
                    count = level
            else:
                text = td.get("aria-label", "") or td.get_text(strip=True)
                m = re.search(r"(\d+)\s+contribution", text)
                if m:
                    count = int(m.group(1))
                else:
                    count = 1 if level > 0 else 0
            days.append({
                "date": d_date,
                "count": count,
                "level": level
            })

    # Regex fallback if BeautifulSoup is missing or returned no data
    if not days:
        tooltips = {}
        for m in re.finditer(r'<tool-tip[^>]*for=\"([^\"]+)\"[^>]*>(.*?)</tool-tip>', html, re.DOTALL):
            for_id = m.group(1)
            text = m.group(2).strip()
            tooltips[for_id] = text

        for m in re.finditer(r'<td[^>]*data-date=\"(\d{4}-\d{2}-\d{2})\"[^>]*>', html):
            cell_tag = m.group(0)
            c_date = m.group(1)

            id_m = re.search(r'id=\"([^\"]+)\"', cell_tag)
            lvl_m = re.search(r'data-level=\"(\d+)\"', cell_tag)

            elem_id = id_m.group(1) if id_m else None
            level = int(lvl_m.group(1)) if lvl_m else 0

            count = 0
            if elem_id and elem_id in tooltips:
                tip_text = tooltips[elem_id]
                cnt_m = re.search(r'(\d+)\s+contribution', tip_text)
                if cnt_m:
                    count = int(cnt_m.group(1))
                elif 'No contribution' in tip_text or '0 contribution' in tip_text:
                    count = 0
                else:
                    count = 1 if level > 0 else 0
            else:
                count = 1 if level > 0 else 0

            days.append({"date": c_date, "count": count, "level": level})

    # Deduplicate and sort by date ascending
    unique_days = {d["date"]: d for d in days}
    sorted_days = [unique_days[k] for k in sorted(unique_days.keys())]
    return sorted_days


def calculate_stats(days):
    if not days:
        return {
            "total_contributions": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": {"date": None, "count": 0},
            "monthly_totals": {},
        }

    sorted_days = sorted(days, key=lambda x: x["date"])
    total = sum(d["count"] for d in sorted_days)

    best_day = max(sorted_days, key=lambda x: x["count"], default={"date": None, "count": 0})

    # Longest streak calculation
    longest_streak = 0
    temp_streak = 0
    for d in sorted_days:
        if d["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Current streak calculation (backwards from latest day)
    i = len(sorted_days) - 1
    if i >= 0 and sorted_days[i]["count"] == 0:
        if i - 1 >= 0 and sorted_days[i - 1]["count"] > 0:
            i -= 1

    c_streak = 0
    while i >= 0 and sorted_days[i]["count"] > 0:
        c_streak += 1
        i -= 1
    current_streak = c_streak

    # Monthly totals
    monthly = {}
    for d in sorted_days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best_day["date"], "count": best_day["count"]},
        "monthly_totals": monthly,
    }


def main():
    print(f"[*] Fetching contribution calendar for {USERNAME}...")
    try:
        html = fetch_html()
        days = parse_contributions(html)
        if not days:
            print("[!] Error: Could not parse contribution days from GitHub HTML.", file=sys.stderr)
            sys.exit(1)

        stats = calculate_stats(days)
        result = {
            "username": USERNAME,
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "stats": stats,
            "days": days
        }

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[✓] Saved {len(days)} days of contributions to {OUTPUT_FILE}")
        print(f"    Total: {stats['total_contributions']} | Current Streak: {stats['current_streak']} | Longest Streak: {stats['longest_streak']}")
        return 0
    except Exception as e:
        print(f"[x] Error fetching contributions: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

