# How to Update LinkedIn Posts on Your Portfolio

This guide explains how to easily add new featured technical posts to your portfolio whenever you post on LinkedIn.

---

## Method 1: The Interactive CLI Tool (Recommended — 30 Seconds)

We built an interactive helper script in your project root.

1. Open your terminal in the portfolio folder and run:
   ```bash
   python3 scripts/add_post.py
   ```

2. The script will prompt you for 4 quick things:
   - **Post Title / Headline**: (e.g., `Solving Concurrency Contention in Django with PostgreSQL Row Locks`)
   - **Technical Summary / Takeaway**: (2-3 sentences summarizing the engineering problem & solution)
   - **LinkedIn Post URL**: (paste your LinkedIn post link)
   - **Tags**: (comma-separated, e.g., `POSTGRESQL, DJANGO, CONCURRENCY`)

3. The script automatically calculates the reading time, formats the entry, and prepends it to `data/featured_posts.json`.

4. Push your update to GitHub:
   ```bash
   git add data/featured_posts.json
   git commit -m "feat(posts): add new engineering post"
   git push
   ```
   Your portfolio will immediately display the new post!

---

## Method 2: Direct JSON Editing

You can also directly edit [`data/featured_posts.json`](../data/featured_posts.json).

Each post follows this clean structure:

```json
{
  "id": "post-03",
  "date": "NOV 2026",
  "readTime": "3 MIN READ",
  "tag": "POSTGRESQL",
  "tags": ["POSTGRESQL", "DATABASE", "PERFORMANCE"],
  "title": "Your Post Headline",
  "content": "A 2 to 3 sentence takeaway describing the system architecture or lesson learned.",
  "mediaType": "image",
  "imageUrl": "https://media.licdn.com/dms/image/...",
  "linkedinUrl": "https://www.linkedin.com/posts/adhil-cr_..."
}
```

### Media Types Supported:
* **Video post**: Set `"mediaType": "video"` and set `"imageUrl"` to the video thumbnail. The card will render a stylish `VIDEO POST ▶` brutalist overlay.
* **Image post**: Set `"mediaType": "image"` and set `"imageUrl"` to the image link.
* **Text-only post**: Set `"imageUrl": null`.

---

## Pro Tip for High-Impact Portfolios
Hiring managers love seeing **real backend lessons**:
* Focus on *challenges faced* and *how you solved them* (e.g., database locks, memory usage, algorithm bottlenecks, caching).
* Keep the summary concise (2–3 sentences) and let the "Read Original Post on LinkedIn →" button drive recruiters directly to your LinkedIn profile.
