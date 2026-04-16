"""Main entry point: fetch, filter, generate, push to GitHub."""

import os
import sys

def main():
    from fetcher import fetch_all_sources
    from filter import filter_and_categorize
    from generator import generate_site

    print("Fetching RSS feeds...")
    raw_items = fetch_all_sources()
    print(f"  -> {len(raw_items)} raw items fetched")

    print("Filtering and categorizing...")
    filtered_items = filter_and_categorize(raw_items)
    print(f"  -> {len(filtered_items)} items after filtering")

    print("Generating HTML site...")
    html = generate_site()

    # Write to index.html in repo root
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  -> Written to {output_path}")

    # Commit & push if GH_TOKEN is set (i.e., running in GitHub Actions)
    token = os.getenv("GH_TOKEN")
    if token:
        print("GH_TOKEN found, committing and pushing...")
        import subprocess
        subprocess.run(["git", "add", "index.html"], check=True)
        result = subprocess.run(
            ["git", "commit", "-m", f"docs: auto-update {__import__('datetime').date.today()}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            subprocess.run(
                ["git", "push", "https://x-access-token:{token}@github.com/wllion821/daily-food-news.git", "main"],
                check=True
            )
            print("  -> Pushed to GitHub")
        else:
            print(f"  -> Nothing to commit (no changes)")
    else:
        print("  -> GH_TOKEN not set, skipping push (local run)")

    print("Done.")


if __name__ == "__main__":
    main()
