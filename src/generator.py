"""Generate static HTML site from filtered news items."""

from datetime import datetime
from filter import filter_and_categorize
from fetcher import fetch_all_sources
from config import CATEGORIES

MAX_ITEMS_PER_COLUMN = 5

# Sub-column definitions per category
# Each entry: (sub_col_key, sub_col_name, filter_fn)
def get_sub_columns(item):
    """Determine which sub-columns an item belongs to."""
    cols = []
    title = item.get("title", "")
    summary = item.get("summary", "")
    brand = item.get("brand", "")

    # 宾堡集团新闻 sub-column
    if "宾堡" in brand or "Bimbo" in brand:
        cols.append(("bimbo", "宾堡集团新闻"))

    # 竞品新闻 sub-column (non-Bimbo brands)
    else:
        cols.append(("competitor", "竞品新闻"))

    # 政策/行业 sub-column (policy/signal items)
    signals = item.get("signals", [])
    if "政策监管" in signals or "行业活动" in signals:
        cols.append(("policy", "食品行业政策新闻"))
    elif item.get("tier") == 1:  # Tier 1 = food safety sources
        cols.append(("policy", "食品行业政策新闻"))

    return cols


def generate_site():
    """Main entry point: fetch, filter, generate."""
    # Fetch and filter
    raw_items = fetch_all_sources()
    filtered_items = filter_and_categorize(raw_items)

    # Build structure: {category: {sub_col: []}}
    categorized = {cat[0]: {"bimbo": [], "competitor": [], "policy": []} for cat in CATEGORIES}

    for item in filtered_items:
        cols = get_sub_columns(item)
        for col_key, col_name in cols:
            for cat_name, cat_desc in CATEGORIES:
                # Simple assignment: first match
                if len(categorized[cat_name][col_key]) < MAX_ITEMS_PER_COLUMN:
                    categorized[cat_name][col_key].append(item)
                    break

    # Generate HTML
    today = datetime.now().strftime("%Y年%m月%d日")
    html = build_html(today, categorized)
    return html


def build_html(date_str, categorized):
    """Build full HTML page."""
    categories_html = ""
    for cat_name, cat_desc in CATEGORIES:
        cols = categorized[cat_name]
        bimbo_items = cols["bimbo"]
        comp_items = cols["competitor"]
        policy_items = cols["policy"]

        if not bimbo_items and not comp_items and not policy_items:
            continue

        categories_html += f"""
        <section class="category">
            <h2>{cat_name}</h2>
            <p class="cat-desc">{cat_desc}</p>
            <div class="sub-columns">
                <div class="sub-col">
                    <h3>宾堡集团新闻</h3>
                    {render_items(bimbo_items)}
                </div>
                <div class="sub-col">
                    <h3>竞品新闻</h3>
                    {render_items(comp_items)}
                </div>
                <div class="sub-col">
                    <h3>食品行业政策新闻</h3>
                    {render_items(policy_items)}
                </div>
            </div>
        </section>
        """
    return HTML_TEMPLATE.format(date=date_str, categories=categories_html)


def render_items(items):
    """Render a list of news items as HTML."""
    if not items:
        return "<p class='empty'>暂无</p>"
    html = ""
    for item in items[:MAX_ITEMS_PER_COLUMN]:
        signals = ", ".join(item.get("signals", []))
        html += f"""
        <article class="news-item">
            <h4><a href="{item['link']}" target="_blank">{item['title']}</a></h4>
            <p class="summary">{item.get('summary', '')}</p>
            <footer>
                <span class="source">{item['source_name']}</span>
                <span class="signals">{signals}</span>
            </footer>
        </article>
        """
    return html


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Food News — 烘焙食品行业情报 {date}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e6e6e6; line-height: 1.6; }}
        header {{ background: linear-gradient(135deg, #1a1f2e, #2d1f3d); padding: 40px 20px; text-align: center; border-bottom: 1px solid #2a2a3a; }}
        header h1 {{ font-size: 2em; color: #f0b90b; margin-bottom: 8px; }}
        header .subtitle {{ color: #888; font-size: 0.95em; }}
        header .date {{ color: #666; font-size: 0.85em; margin-top: 8px; }}
        main {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
        .category {{ background: #1a1f2e; border-radius: 12px; padding: 24px; margin-bottom: 24px; border: 1px solid #2a2a3a; }}
        .category h2 {{ color: #f0b90b; font-size: 1.4em; margin-bottom: 4px; }}
        .cat-desc {{ color: #666; font-size: 0.85em; margin-bottom: 20px; }}
        .sub-columns {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .sub-col {{ background: #12151e; border-radius: 8px; padding: 16px; border: 1px solid #2a2a3a; }}
        .sub-col h3 {{ color: #e0c060; font-size: 1em; margin-bottom: 12px; border-bottom: 1px solid #2a2a3a; padding-bottom: 8px; }}
        .news-item {{ margin-bottom: 16px; }}
        .news-item h4 {{ font-size: 0.95em; margin-bottom: 4px; }}
        .news-item h4 a {{ color: #e6e6e6; text-decoration: none; }}
        .news-item h4 a:hover {{ color: #f0b90b; }}
        .news-item .summary {{ font-size: 0.82em; color: #888; margin-bottom: 4px; }}
        .news-item footer {{ font-size: 0.75em; color: #555; }}
        .news-item footer .source {{ margin-right: 8px; }}
        .news-item footer .signals {{ color: #7a6a4a; }}
        .empty {{ color: #444; font-size: 0.85em; text-align: center; padding: 20px 0; }}
        footer {{ text-align: center; color: #444; font-size: 0.8em; padding: 30px; border-top: 1px solid #1a1f2e; margin-top: 40px; }}
        @media (max-width: 768px) {{ .sub-columns {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <header>
        <h1>Daily Food News</h1>
        <div class="subtitle">烘焙食品行业情报</div>
        <div class="date">{date}</div>
    </header>
    <main>
        {categories}
    </main>
    <footer>
        每日更新 · 数据来源：人工筛选优质信源
    </footer>
</body>
</html>
"""


if __name__ == "__main__":
    html = generate_site()
    output_path = "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {output_path}")
