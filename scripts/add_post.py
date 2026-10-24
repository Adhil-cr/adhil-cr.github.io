#!/usr/bin/env python3
"""
add_post.py
Helper tool to easily add a curated engineering post to data/featured_posts.json.
Can be used interactively or with command-line flags.

Usage:
    python3 scripts/add_post.py
    or
    python3 scripts/add_post.py --title "My Title" --content "Takeaway summary" --url "https://linkedin.com/posts/..." --tags "DJANGO,POSTGRESQL"
"""

import os
import sys
import json
import argparse
from datetime import datetime

POSTS_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "featured_posts.json")
)
DEFAULT_LINKEDIN = "https://www.linkedin.com/in/adhil-cr"


def compute_read_time(text: str) -> str:
    words = len(text.split())
    minutes = max(1, round(words / 150))
    return f"{minutes} MIN READ"


def main():
    parser = argparse.ArgumentParser(description="Add a featured post to portfolio data")
    parser.add_argument("--title", help="Post headline/title")
    parser.add_argument("--content", help="Brief plain-English engineering takeaway (2-3 sentences)")
    parser.add_argument("--url", help="Direct URL to original LinkedIn post")
    parser.add_argument("--tags", help="Comma-separated tags (e.g. DJANGO,POSTGRESQL)")
    parser.add_argument("--date", help="Month/Year label (e.g. OCT 2026)")
    parser.add_argument("--image", help="Image or video thumbnail URL")
    parser.add_argument("--video", help="Direct MP4 video URL or path")
    parser.add_argument("--media-type", choices=["image", "video"], help="Type of media (image or video)")
    args = parser.parse_args()

    # Read existing
    existing = []
    if os.path.exists(POSTS_FILE):
        try:
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception as e:
            print(f"Warning: could not read {POSTS_FILE}: {e}")

    # Interactive prompt if flags not passed
    title = args.title
    if not title:
        print("\n--- Add Curated Technical Post to Portfolio ---")
        title = input("1. Post Title / Headline: ").strip()
        if not title:
            print("Error: Title is required.")
            sys.exit(1)

    content = args.content
    if not content:
        content = input("2. Technical Summary / Takeaway (2-3 sentences): ").strip()
        if not content:
            print("Error: Content summary is required.")
            sys.exit(1)

    url = args.url
    if not url:
        raw_url = input(f"3. LinkedIn Post URL (Enter for {DEFAULT_LINKEDIN}): ").strip()
        url = raw_url if raw_url else DEFAULT_LINKEDIN

    tags_input = args.tags
    if not tags_input:
        raw_tags = input("4. Tags (comma-separated, e.g. DJANGO, POSTGRESQL): ").strip()
        tags_input = raw_tags if raw_tags else "BACKEND, SYSTEMS"

    tags = [t.strip().upper() for t in tags_input.split(",") if t.strip()]
    if not tags:
        tags = ["BACKEND"]

    date_str = args.date
    if not date_str:
        date_str = datetime.now().strftime("%b %Y").upper()

    read_time = compute_read_time(content)

    image_url = args.image
    video_url = args.video
    media_type = args.media_type
    if not image_url and not video_url and not args.title: # only prompt interactively if running in interactive mode
        raw_img = input("5. Image/Thumbnail URL (optional, press Enter to skip): ").strip()
        if raw_img:
            image_url = raw_img
            raw_type = input("   Media Type (image/video, default: image): ").strip().lower()
            media_type = "video" if raw_type == "video" else "image"
            if media_type == "video":
                raw_vid = input("   Direct MP4 Video URL (optional, press Enter to skip): ").strip()
                if raw_vid:
                    video_url = raw_vid

    new_post = {
        "id": f"post-{len(existing) + 1:02d}",
        "date": date_str,
        "readTime": read_time,
        "tag": tags[0],
        "tags": tags,
        "title": title,
        "content": content,
        "mediaType": media_type,
        "videoUrl": video_url,
        "imageUrl": image_url,
        "linkedinUrl": url
    }

    # Prepend new post
    updated = [new_post] + existing

    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n✓ Successfully added '{title}' to {POSTS_FILE}!")
    print(f"Total featured posts: {len(updated)}")


if __name__ == "__main__":
    main()
