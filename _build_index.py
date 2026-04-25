#!/usr/bin/env python3
"""
_build_index.py
---------------
Regenerate the top-level index.html for the unified MStreet-Global-Pages site.

Walks immediate subfolders of this repo (each = one plugin), counts skills
(sub-subfolders containing HTML files), finds the latest modification time,
and emits a card-style landing page linking to each plugin's own index.html.

Usage (from this folder, ~/Desktop/MStreet-Global-Pages):
    python _build_index.py

Run automatically:
    Each plugin's publish_to_pages helper invokes this after writing per-plugin
    indexes, so the landing page stays current with every publish.

Output: index.html in the same directory as this script.
"""
from __future__ import annotations

import sys
from datetime import datetime
from html import escape
from pathlib import Path

# Folders to exclude from plugin enumeration
EXCLUDED = {".git", ".github", ".claude", "node_modules", "__pycache__"}


def discover_plugins(root: Path) -> list[dict]:
    """Walk immediate subfolders; return one dict per plugin with stats."""
    plugins = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        if entry.name in EXCLUDED:
            continue

        # Count skills, reports, and find latest mtime — recursing through
        # any depth of intermediate folders (e.g. std-cov-cor/<family>/*.html).
        # A "skill" is an immediate subfolder of `entry` containing at least
        # one non-index .html file (anywhere within).
        skill_count = 0
        report_count = 0
        latest_mtime = 0.0
        for skill_dir in entry.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            html_files = [
                f for f in skill_dir.rglob("*.html")
                if f.is_file() and f.name != "index.html"
            ]
            if html_files:
                skill_count += 1
                report_count += len(html_files)
                for f in html_files:
                    latest_mtime = max(latest_mtime, f.stat().st_mtime)

        plugins.append({
            "name": entry.name,
            "skills": skill_count,
            "reports": report_count,
            "latest_mtime": latest_mtime,
            "has_index": (entry / "index.html").exists(),
        })
    return plugins


def build_index_html(plugins: list[dict]) -> str:
    """Render the landing page HTML."""
    cards = []
    for p in plugins:
        if p["latest_mtime"] > 0:
            latest_str = datetime.fromtimestamp(p["latest_mtime"]).strftime("%Y-%m-%d %H:%M")
        else:
            latest_str = "(no reports yet)"

        link_target = f"{escape(p['name'])}/index.html" if p["has_index"] else f"{escape(p['name'])}/"
        body = (
            f'<div class="card">'
            f'<h2><a href="{link_target}">{escape(p["name"])}</a></h2>'
            f'<dl>'
            f'<dt>Skills</dt><dd>{p["skills"]}</dd>'
            f'<dt>Reports</dt><dd>{p["reports"]}</dd>'
            f'<dt>Latest</dt><dd>{escape(latest_str)}</dd>'
            f'</dl>'
            f'</div>'
        )
        cards.append(body)

    cards_html = "\n".join(cards) if cards else '<p class="empty">No plugins yet.</p>'
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MStreet Global Pages</title>
<style>
  :root {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           --fg: #1a1a1a; --muted: #777; --accent: #003366; --bg: #fafafa; --card: #fff;
           --border: #e0e0e0; }}
  body {{ max-width: 900px; margin: 40px auto; padding: 0 20px;
         background: var(--bg); color: var(--fg); line-height: 1.5; }}
  header {{ border-bottom: 2px solid var(--accent); padding-bottom: 12px; margin-bottom: 24px; }}
  h1 {{ margin: 0; color: var(--accent); font-size: 28px; }}
  .subtitle {{ color: var(--muted); margin-top: 4px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 6px;
          padding: 16px 20px; }}
  .card h2 {{ margin: 0 0 8px 0; font-size: 18px; }}
  .card h2 a {{ color: var(--accent); text-decoration: none; }}
  .card h2 a:hover {{ text-decoration: underline; }}
  dl {{ margin: 8px 0 0 0; display: grid; grid-template-columns: max-content 1fr;
        gap: 4px 12px; font-size: 14px; }}
  dt {{ color: var(--muted); }}
  dd {{ margin: 0; }}
  .empty {{ color: var(--muted); font-style: italic; }}
  footer {{ margin-top: 32px; padding-top: 12px; border-top: 1px solid var(--border);
            color: var(--muted); font-size: 12px; }}
</style>
</head>
<body>
<header>
  <h1>MStreet Global Pages</h1>
  <div class="subtitle">Unified report site for the MStreet plugin suite</div>
</header>
<main>
  <div class="grid">
{cards_html}
  </div>
</main>
<footer>
  Generated {generated} by <code>_build_index.py</code>
</footer>
</body>
</html>
"""


def main():
    here = Path(__file__).resolve().parent
    plugins = discover_plugins(here)
    html = build_index_html(plugins)
    out = here / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}  ({len(plugins)} plugins, "
          f"{sum(p['reports'] for p in plugins)} total reports)")


if __name__ == "__main__":
    main()
