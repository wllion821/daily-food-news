"""Fetch RSS feeds from all configured sources."""

import feedparser
from datetime import datetime
from config import SOURCES


def fetch_all_sources():
    """Fetch all RSS feeds, return list of news items."""
    all_items = []

    for source_id, source in SOURCES.items():
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries:
                item = {
                    "source_id": source_id,
                    "source_name": source["name"],
                    "tier": source["tier"],
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": strip_html(entry.get("summary", "")),
                    "published": entry.get("published", ""),
                    "fetched_at": datetime.now().isoformat(),
                }
                all_items.append(item)
        except Exception as e:
            print(f"Error fetching {source_id}: {e}")

    return all_items


def strip_html(text):
    """Remove HTML tags from text."""
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


if __name__ == "__main__":
    items = fetch_all_sources()
    print(f"Fetched {len(items)} items from {len(SOURCES)} sources")
