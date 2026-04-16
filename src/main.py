"""
Main entry point: fetch sources → fetch article content → filter → generate → push.
"""

import os, sys, time
from datetime import datetime

def main():
    from src.fetcher import fetch_all_sources, fetch_article_content
    from src.filter import filter_and_categorize
    from src.generator import generate_site
    from src.config import SOURCES
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Fetching article links from {len(SOURCES)} sources...")
    raw_items = fetch_all_sources()
    print(f"  → {len(raw_items)} raw article links")

    # Filter: only sources that returned articles
    active_sources = list(dict.fromkeys(item['source_id'] for item in raw_items))
    print(f"  → Active sources: {active_sources}")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 2: Fetching article content (this takes ~2-3 min)...")
    detailed_items = []
    for i, item in enumerate(raw_items):
        if i % 20 == 0:
            print(f"  → [{i}/{len(raw_items)}]")
        d = fetch_article_content(item)
        if d.get('title'):  # Only keep articles where we actually got content
            detailed_items.append(d)
        time.sleep(0.15)  # polite delay between requests
    print(f"  → {len(detailed_items)} articles with content")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 3: Filtering and categorizing...")
    filtered = filter_and_categorize(detailed_items)
    print(f"  → {len(filtered)} articles passed filter")

    if not filtered:
        print("  [WARNING] No articles passed filter. Check brand keywords and signal scores.")
        # Fall back: show top signal-scored articles even without brand match
        from filter import get_signal_score
        scored = [(get_signal_score(i.get('title',''), i.get('summary','')), i) for i in detailed_items]
        scored.sort(key=lambda x: x[0][0], reverse=True)
        filtered = [i for score, i in scored[:30]]  # take top 30 by signal score
        print(f"  → Using top {len(filtered)} by signal score (no brand match required)")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 4: Generating HTML site...")
    html = generate_site(filtered)

    # Write to index.html
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  → Written to {output_path}")

    # Commit & push if in GitHub Actions
    token = os.getenv("GH_TOKEN")
    if token:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Step 5: Committing and pushing...")
        import subprocess
        git_cmds = [
            ["git", "add", "index.html"],
            ["git", "config", "user.name", "github-actions[bot]"],
            ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
        ]
        for cmd in git_cmds:
            subprocess.run(cmd, capture_output=True)

        result = subprocess.run(
            ["git", "commit", "-m", f"docs: auto-update {datetime.now().strftime('%Y-%m-%d')}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            push_result = subprocess.run(
                ["git", "push",
                 f"https://x-access-token:{token}@github.com/wllion821/daily-food-news.git", "main"],
                capture_output=True, text=True
            )
            if push_result.returncode == 0:
                print("  → Pushed to GitHub")
            else:
                print(f"  → Push failed: {push_result.stderr[:200]}")
        else:
            print(f"  → Nothing to commit (no changes)")
    else:
        print(f"\n  → GH_TOKEN not set, skipping push (local run)")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Done.")


if __name__ == "__main__":
    main()
