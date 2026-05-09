"""
Fetch article links and content from verified scrapable sources using curl.
Uses subprocess to call curl with proper headers and SSL bypass.
"""

import subprocess, re, json, os
from datetime import datetime
from .config import SOURCES


CURL_TIMEOUT = 12  # seconds per source


def fetch_source(source_id: str, source: dict) -> list:
    """Fetch article links from a source homepage, return list of article dicts."""
    url = source["url"]
    name = source["name"]
    pattern = source.get("article_pattern", r"/\d+\.html")

    cmd = [
        "curl", "-s", "--max-time", str(CURL_TIMEOUT),
        "-L", "-A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "-H", "Accept-Language: zh-CN,zh;q=0.9",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=CURL_TIMEOUT + 2)
        html = result.stdout
    except subprocess.TimeoutExpired:
        print(f"  [timeout] {source_id}")
        return []
    except Exception as e:
        print(f"  [error] {source_id}: {e}")
        return []

    if not html or len(html) < 200:
        return []

    # Extract article links matching the pattern
    all_links = re.findall(r'href="([^"]+)"', html)
    article_links = []
    for link in all_links:
        # Skip non-article links
        if any(x in link.lower() for x in ["javascript", "void", "login", "register", "about", "contact", "privacy", "subscribe", "feed", "rss", "sitemap"]):
            continue
        # Resolve relative URLs
        if link.startswith("//"):
            link = "https:" + link
        elif link.startswith("/"):
            # Extract domain from URL
            domain = re.match(r'(https?://[^/]+)', url)
            if domain:
                link = domain.group(1) + link
        # Check if matches article pattern
        if re.search(pattern, link) and (link.startswith("http")):
            article_links.append(link)

    # Deduplicate and limit
    article_links = list(dict.fromkeys(article_links))[:20]

    items = []
    for link in article_links:
        item = {
            "source_id": source_id,
            "source_name": name,
            "tier": source["tier"],
            "link": link,
            "fetched_at": datetime.now().isoformat(),
        }
        items.append(item)

    if items:
        print(f"  [{len(items)} articles] {source_id} ({name})")
    else:
        print(f"  [0 articles] {source_id} ({name})")

    return items


def fetch_article_content(item: dict) -> dict:
    """Fetch a single article page and extract title + summary."""
    link = item["link"]
    cmd = [
        "curl", "-s", "--max-time", str(CURL_TIMEOUT),
        "-L", "-A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "-H", "Accept-Language: zh-CN,zh;q=0.9",
        link,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=CURL_TIMEOUT + 2)
        html = result.stdout
    except Exception:
        return {**item, "title": "", "summary": ""}

    if not html or len(html) < 200:
        return {**item, "title": "", "summary": ""}

    # Extract title: <title>...</title> or <h1>...</h1>
    title = ""
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if m:
        title = re.sub(r'\s+', ' ', m.group(1).strip())

    # Extract meta description
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if m:
        summary = m.group(1).strip()
    else:
        # Try to find first paragraph
        m = re.search(r'<p[^>]*>([^<]{20,500})</p>', html, re.IGNORECASE)
        summary = m.group(1).strip() if m else ""

    # Clean HTML tags
    title = re.sub(r'<[^>]+>', '', title)
    summary = re.sub(r'<[^>]+>', '', summary)
    summary = re.sub(r'\s+', ' ', summary).strip()

    return {**item, "title": title[:200], "summary": summary[:500]}


def fetch_all_sources() -> list:
    """Fetch all sources, return list of raw article items."""
    print(f"Fetching {len(SOURCES)} sources...")
    all_items = []
    for source_id, source in SOURCES.items():
        items = fetch_source(source_id, source)
        all_items.extend(items)
    print(f"Total raw articles: {len(all_items)}")
    return all_items


def fetch_article_details(items: list) -> list:
    """Fetch content for a batch of articles. Returns updated items with title/summary."""
    print(f"Fetching details for {len(items)} articles...")
    detailed = []
    for i, item in enumerate(items):
        if i % 10 == 0:
            print(f"  [{i}/{len(items)}]")
        detailed.append(fetch_article_content(item))
    return detailed


if __name__ == "__main__":
    items = fetch_all_sources()
    print(f"\nFetched {len(items)} raw items")
    for item in items[:5]:
        print(f"  - {item['source_name']}: {item['link']}")
