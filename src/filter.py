"""Filter news items based on brand keywords, signal keywords, and exclusion rules."""

from config import BRAND_KEYWORDS, SIGNAL_KEYWORDS, EXCLUDE_KEYWORDS, CATEGORIES


def is_brand_mentioned(title, summary=""):
    """Check if any brand keyword is mentioned."""
    text = (title + " " + summary).lower()
    for brand, keywords in BRAND_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                return brand
    return None


def get_signal_score(title, summary=""):
    """Calculate signal score based on keyword matches."""
    text = (title + " " + summary).lower()
    score = 0
    matched_signals = []

    # Brand match: high priority
    if is_brand_mentioned(title, summary):
        score += 10

    # Signal keywords
    for category, keywords in SIGNAL_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                score += 1
                matched_signals.append(category)

    return score, list(set(matched_signals))


def should_exclude(title, summary=""):
    """Check if item should be excluded."""
    text = (title + " " + summary).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in text:
            return True
    return False


def filter_and_categorize(items):
    """Filter items by rules, then categorize into 5 major categories."""
    filtered = []

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")

        # Skip excluded
        if should_exclude(title, summary):
            continue

        # Must mention a brand (Bimbo or competitor)
        brand = is_brand_mentioned(title, summary)
        if not brand:
            continue

        score, signals = get_signal_score(title, summary)

        filtered.append({
            **item,
            "brand": brand,
            "signal_score": score,
            "signals": signals,
        })

    # Sort by score descending
    filtered.sort(key=lambda x: x["signal_score"], reverse=True)

    return filtered


if __name__ == "__main__":
    from fetcher import fetch_all_sources
    items = fetch_all_sources()
    filtered = filter_and_categorize(items)
    print(f"Filtered {len(filtered)} items from {len(items)} total")
