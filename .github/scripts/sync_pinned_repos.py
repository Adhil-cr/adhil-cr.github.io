#!/usr/bin/env python3
"""
sync_pinned_repos.py
Scrapes and parses the author's live pinned repositories from https://github.com/Adhil-cr,
fetches repository 'homepage' (live URL from About section), and updates data/pinned_repos.json cleanly.
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

# Curated fallback titles and descriptions for repos
CURATED_METADATA = {
    "seating-system": {
        "name": "ExamCell Automation System",
        "description": "High-integrity examination hall and matrix seating engine in Django & PostgreSQL that normalizes enrollments and generates deterministic seating plans.",
        "tech": ["Python 3.12", "Django", "PostgreSQL", "Pandas"],
        "homepage": "https://benchmap.in/"
    },
    "E-Commerce-Web": {
        "name": "Core Commerce Service",
        "description": "Transactional Django commerce backend enforcing ACID database transactions with row-level locking (SELECT FOR UPDATE) to eliminate checkout race conditions.",
        "tech": ["Python 3.12", "Django REST", "PostgreSQL", "ACID Transactions"],
        "homepage": ""
    },
    "Daily-python": {
        "name": "Systems & Algorithms Lab",
        "description": "Comprehensive 9-tier software engineering repository exploring low-level C memory patterns, pointer arithmetic, and cache-conscious Python internals.",
        "tech": ["Python 3.12", "C Programming", "Data Structures", "Memory Profiling"],
        "homepage": ""
    },
    "BroComplaint": {
        "name": "BroComplaint Portal",
        "description": "Student grievance and administrative tracking portal engineered with TypeScript, modular routing, and role-based access control.",
        "tech": ["TypeScript", "Fullstack", "RBAC", "REST"],
        "homepage": "https://brototype-issue-tracker.lovable.app"
    }
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


def fetch_repo_homepage(repo_name):
    """Fetch repo homepage (live link in About section) via GitHub REST API."""
    api_url = f"https://api.github.com/repos/{USERNAME}/{repo_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/vnd.github.v3+json"
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hp = data.get("homepage")
            if hp and isinstance(hp, str) and hp.strip():
                return hp.strip()
    except Exception as e:
        print(f"Notice: GitHub API homepage lookup for {repo_name} skipped ({e})")
    return ""


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

        curated = CURATED_METADATA.get(repo_name, {})
        raw_desc = re.sub(r"<.*?>", "", desc_match.group(1)).strip() if desc_match else ""
        desc = curated.get("description") or raw_desc or "Backend systems repository."
        name = curated.get("name") or repo_name
        tech = curated.get("tech") or ["Backend"]
        lang = lang_match.group(1).strip() if lang_match else "Python"
        color = color_match.group(1).strip() if color_match else LANGUAGE_COLORS.get(lang, "#FF6D1F")
        stars = int(stars_match.group(1)) if stars_match else 0

        # Query live homepage / website from GitHub repo About section
        homepage = fetch_repo_homepage(repo_name) or curated.get("homepage", "")

        repos.append({
            "repo": repo_name,
            "name": name,
            "link": f"https://github.com/{USERNAME}/{repo_name}",
            "homepage": homepage,
            "description": desc,
            "language": lang,
            "languageColor": color,
            "tech": tech,
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
        hp_info = f" [Live: {r['homepage']}]" if r.get('homepage') else ""
        print(f"  - {r['repo']} ({r['language']}){hp_info}")

    # Write update
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pinned, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Successfully saved pinned repos to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
