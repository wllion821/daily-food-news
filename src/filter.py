"""Filter news items based on brand keywords and signal keywords."""

from .config import BRAND_KEYWORDS, SIGNAL_KEYWORDS


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
    brand = is_brand_mentioned(title, summary)
    if brand:
        score += 10

    # Signal keywords
    for category, keywords in SIGNAL_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                score += 1
                matched_signals.append(category)

    return score, list(set(matched_signals)), brand


def filter_and_categorize(items):
    """
    Pass items that either:
    1. Mention a brand keyword (Bimbo or competitor), OR
    2. Have signal score >= 3 (food safety regulation, industry events)

    All passed items get categorized into sub-columns.
    """
    filtered = []

    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")

        score, signals, brand = get_signal_score(title, summary)

        # Pass if brand match OR strong signal
        if brand or score >= 3:
            filtered.append({
                **item,
                "brand": brand or "食品行业",
                "signal_score": score,
                "signals": signals,
            })

    # Sort by score descending
    filtered.sort(key=lambda x: x["signal_score"], reverse=True)

    return filtered


if __name__ == "__main__":
    from src.fetcher import fetch_all_sources
    items = fetch_all_sources()
    filtered = filter_and_categorize(items)
    print(f"Filtered {len(filtered)} items from {len(items)} total")
