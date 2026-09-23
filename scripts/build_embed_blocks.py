#!/usr/bin/env python3
"""Split site/index.html into small blocks for Google Sites "Embed code".

A single long embed scrolls inside its frame, so the page is cut into
sections, each pasted as its own Embed block stacked down the Google Sites
page. Photos load from the GitHub Pages copy of the site. Output: embed/*.html
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "index.html"
OUT = ROOT / "embed"
IMAGE_BASE = "https://b69s.github.io/eis-facility/images/"

html = SRC.read_text(encoding="utf-8")
head_links = "\n".join(re.findall(r'<link [^>]*>', html))
css = re.search(r"<style>(.*?)</style>", html, re.S).group(1)

# Each block is its own frame: drop the between-section spacing the full page
# used, and give every block the same small top/bottom breathing room.
EMBED_CSS = """
  body { padding: 16px 0 24px; }
  .page { padding: 0 24px; }
  header, #message, #completed, #progress { padding-top: 0; }
  #learning, #future { margin-top: 0; }
  .block > .group-head:first-child { margin-top: 0; }
"""


def between(start, end, include_end=True):
    i = html.index(start)
    j = html.index(end, i) + (len(end) if include_end else 0)
    return html[i:j]


completed = between('<section id="completed">', "</section>")
inner = completed[len('<section id="completed">'):-len("</section>")]
heads = [m.start() for m in re.finditer(r'<div class="group-head', inner)]
# intro + group 01 | group 02 | groups 03–05
parts = [inner[:heads[1]], inner[heads[1]:heads[2]], inner[heads[2]:]]

blocks = [
    ("01-header", "Header and numbers", between("<header>", "</header>")),
    ("02-message", "Message from the Head of School", between('<section id="message">', "</section>")),
    ("03-completed-welcome", "Completed: Welcome & shared spaces", f'<section id="completed">{parts[0]}</section>'),
    ("04-completed-classrooms", "Completed: Classrooms & teaching spaces", f'<section id="completed">{parts[1]}</section>'),
    ("05-completed-more", "Completed: Specialist, wellbeing, comfort", f'<section id="completed">{parts[2]}</section>'),
    ("06-why-it-matters", "How these improvements support learning", between('<section id="learning">', "</section>")),
    ("07-in-progress", "Underway and coming soon", between('<section id="progress">', "</section>")),
    ("08-future-contact", "Future priorities and contact", between('<section id="future">', 'Page updated September 2026</div>')),
]

OUT.mkdir(exist_ok=True)
for slug, _, body in blocks:
    body = body.replace('src="images/', f'src="{IMAGE_BASE}').replace(' loading="lazy"', "")
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{head_links}
<style>{css}{EMBED_CSS}</style>
</head>
<body>
<div class="page"><div class="wrap block">
{body.strip()}
</div></div>
</body>
</html>
"""
    (OUT / f"{slug}.html").write_text(doc, encoding="utf-8")
    print(f"embed/{slug}.html  {len(doc.encode()) / 1024:.1f} KB")
