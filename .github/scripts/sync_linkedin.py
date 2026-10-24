#!/usr/bin/env python3
"""
sync_linkedin.py
Syncs LinkedIn posts into data/featured_posts.json.
Can parse:
1. An RSS / Atom feed URL (e.g., from RSS.app, RSSHub, or FetchRSS) provided via LINKEDIN_RSS_URL.
2. A custom JSON endpoint or webhook.
3. Fallback / validation mode: preserves and validates existing curated posts.
"""

import os
import sys
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

POSTS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "featured_posts.json")
POSTS_FILE = os.path.normpath(POSTS_FILE)

DEFAULT_PROFILE = "https://www.linkedin.com/in/adhil-cr"


def clean_html(raw_html: str) -> str:
    """Strip HTML tags and unescape common HTML entities."""
    cleanr = re.compile(r"<.*?>")
    text = re.sub(cleanr, "", raw_html)
    text = (
        text.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
        .replace("&nbsp;", " ")
    )
    return " ".join(text.split())


def extract_tags(text: str) -> list[str]:
    """Extract hashtags from post content or default to backend topics."""
    hashtags = re.findall(r"#(\w+)", text)
    if hashtags:
        return [h.upper() for h in hashtags[:4]]
    # Keyword inference fallback
    keywords = []
    text_lower = text.lower()
    if "postgres" in text_lower or "sql" in text_lower:
        keywords.append("POSTGRESQL")
    if "django" in text_lower or "orm" in text_lower:
        keywords.append("DJANGO")
    if "python" in text_lower:
        keywords.append("PYTHON")
    if "concurrency" in text_lower or "lock" in text_lower:
        keywords.append("CONCURRENCY")
    if "c " in text_lower or "pointer" in text_lower or "systems" in text_lower:
        keywords.append("SYSTEMS")
    return keywords if keywords else ["ENGINEERING", "BACKEND"]


def calculate_read_time(text: str) -> str:
    """Calculate estimated read time based on word count."""
    words = len(text.split())
    minutes = max(1, round(words / 150))
    return f"{minutes} MIN READ"


def fetch_from_rss(feed_url: str) -> list[dict]:
    """Fetch and parse RSS / Atom feed."""
    req = urllib.request.Request(
        feed_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; PortfolioSync/1.0; +https://adhil-cr.github.io)"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read()

    root = ET.fromstring(content)
    posts = []

    # Handle standard RSS 2.0 channel/item
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else root.findall(".//item")

    # Handle Atom entries if RSS items not found
    if not items:
        items = root.findall("{http://www.w3.org/2005/Atom}entry")

    for item in items:
        # Title
        title_el = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
        title = clean_html(title_el.text) if title_el is not None and title_el.text else "Technical Post"

        # Link
        link_el = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
        link = DEFAULT_PROFILE
        if link_el is not None:
            link = link_el.get("href") or link_el.text or DEFAULT_PROFILE

        # Description / Content
        desc_el = (
            item.find("description")
            or item.find("{http://www.w3.org/2005/Atom}content")
            or item.find("{http://www.w3.org/2005/Atom}summary")
        )
        description = clean_html(desc_el.text) if desc_el is not None and desc_el.text else ""

        # PubDate
        date_el = item.find("pubDate") or item.find("{http://www.w3.org/2005/Atom}updated")
        date_str = "RECENT"
        if date_el is not None and date_el.text:
            try:
                # Try parsing standard RFC 822 or ISO
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(date_el.text)
                date_str = dt.strftime("%b %Y").upper()
            except Exception:
                try:
                    dt = datetime.fromisoformat(date_el.text.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %Y").upper()
                except Exception:
                    date_str = "RECENT"

        tags = extract_tags(description + " " + title)
        read_time = calculate_read_time(description)

        # Truncate content for card view if too verbose
        card_content = description
        if len(card_content) > 320:
            card_content = card_content[:317] + "..."

        posts.append({
            "id": f"post-{abs(hash(link)) % 1000000:06d}",
            "date": date_str,
            "readTime": read_time,
            "tag": tags[0] if tags else "BACKEND",
            "tags": tags,
            "title": title,
            "content": card_content,
            "imageUrl": None,
            "linkedinUrl": link
        })

    return posts


def main():
    feed_url = os.environ.get("LINKEDIN_RSS_URL", "").strip()
    
    existing_posts = []
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                existing_posts = json.load(f)
        except Exception as e:
            print(f"Warning: could not read {POSTS_FILE}: {e}")

    if not feed_url:
        print("LINKEDIN_RSS_URL secret/env not set.")
        print("To enable automatic live sync, set LINKEDIN_RSS_URL in repository secrets with an RSS bridge URL.")
        print(f"Current posts verified ({len(existing_posts)} posts present). Exiting cleanly.")
        # Ensure file is formatted properly
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_posts, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return

    print(f"Fetching updates from RSS feed: {feed_url} ...")
    try:
        new_posts = fetch_from_rss(feed_url)
        print(f"Fetched {len(new_posts)} items from feed.")
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        sys.exit(1)

    if not new_posts:
        print("No items found in feed.")
        return

    # Merge strategy: map existing posts by linkedinUrl
    posts_by_url = {p.get("linkedinUrl"): p for p in existing_posts if p.get("linkedinUrl")}
    
    # Prepend new posts
    merged = []
    added_count = 0
    for p in new_posts:
        url = p.get("linkedinUrl")
        if url and url not in posts_by_url:
            merged.append(p)
            posts_by_url[url] = p
            added_count += 1

    # Append remaining existing posts
    for p in existing_posts:
        if p not in merged:
            merged.append(p)

    print(f"Sync complete. Added {added_count} new posts. Total posts: {len(merged)}")
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
