#!/usr/bin/env python3
"""
sync_pinned_repos.py
Scrapes and parses the author's live pinned repositories from https://github.com/Adhil-cr
and updates data/pinned_repos.json cleanly.
Zero third-party API dependencies, completely free, reliable.
"""

import os
import sys
import re
import json
import urllib.request

USERNAME = "Adhil-cr"
PROFILE_URL = f"https://github.com/{USERNAME}"
OUTPUT_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "pinned_repos.json")
)

# Curated fallback descriptions for repos that might have an empty description on GitHub
CURATED_DESCRIPTIONS = {
    "Daily-python": "Comprehensive 9-tier software engineering journey from Python & C memory fundamentals to production backend architecture.",
    "seating-system": "ExamCell – Examination Hall Seating Arrangement Automation System built with Django, PostgreSQL, SQLite, and PyInstaller.",
    "BroComplaint": "Student grievance and complaint management portal with role-based routing and administrative tracking.",
    "E-Commerce-Web": "Transactional Django E-Commerce backend service featuring cart workflows, soft-deletion, and row-level locking.",
}

# Standard language color fallbacks
LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "C": "#555555",
    "CSS": "#563d7c",
}


def fetch_pinned_repos():
    req = urllib.request.Request(
        PROFILE_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode("utf-8")

    pinned_blocks = re.findall(
        r'<li[^>]*class="[^"]*pinned-item-list-item[^"]*"[^>]*>(.*?)</li>',
        html,
        re.DOTALL
    )

    if not pinned_blocks:
        print("Notice: No pinned repo blocks found in HTML response.")
        return []

    repos = []
    for item in pinned_blocks:
        repo_match = re.search(r'href="/' + re.escape(USERNAME) + r'/([^"]+)"', item, re.IGNORECASE)
        desc_match = re.search(r'<p[^>]*pinned-item-desc[^"]*"[^>]*>(.*?)</p>', item, re.DOTALL)
        lang_match = re.search(r'<span itemprop="programmingLanguage">(.*?)</span>', item)
        color_match = re.search(r'class="repo-language-color" style="background-color:\s*([^;"]+)', item)
        stars_match = re.search(r'href="/' + re.escape(USERNAME) + r'/[^"]+/stargazers"[^>]*>\s*([0-9]+)', item, re.IGNORECASE)

        repo_name = repo_match.group(1).strip() if repo_match else ""
        if not repo_name:
            continue

        raw_desc = re.sub(r"<.*?>", "", desc_match.group(1)).strip() if desc_match else ""
        desc = raw_desc or CURATED_DESCRIPTIONS.get(repo_name, "Backend systems repository.")
        lang = lang_match.group(1).strip() if lang_match else "Python"
        color = color_match.group(1).strip() if color_match else LANGUAGE_COLORS.get(lang, "#FF6D1F")
        stars = int(stars_match.group(1)) if stars_match else 0

        repos.append({
            "repo": repo_name,
            "link": f"https://github.com/{USERNAME}/{repo_name}",
            "description": desc,
            "language": lang,
            "languageColor": color,
            "stars": stars
        })

    return repos


def main():
    print(f"Scraping live pinned repositories from {PROFILE_URL} ...")
    try:
        pinned = fetch_pinned_repos()
    except Exception as e:
        print(f"Error fetching GitHub profile: {e}")
        sys.exit(0)  # Keep build healthy

    if not pinned:
        print("No pinned items parsed. Preserving existing data.")
        return

    print(f"Found {len(pinned)} pinned repositories:")
    for r in pinned:
        print(f"  - {r['repo']} ({r['language']})")

    # Read existing
    existing = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Write update
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pinned, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully saved pinned repos to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
