#!/usr/bin/env python3
"""Build a single self-contained HTML file for Google Sites "Embed code".

Inlines every images/*.webp referenced by site/index.html as a data: URI so
the page needs no separate image hosting. Output: dist/facility-improvements-embed.html
"""
import base64
import mimetypes
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "site" / "index.html"
OUT = ROOT / "dist" / "facility-improvements-embed.html"


def inline(match):
    path = SRC.parent / match.group(1)
    if not path.exists():  # e.g. the commented-out Head of School portrait
        return match.group(0)
    mime = mimetypes.guess_type(path.name)[0] or "image/webp"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'src="data:{mime};base64,{data}"'


html = SRC.read_text(encoding="utf-8")
html = re.sub(r'src="(images/[^"]+)"', inline, html)
# Lazy loading does nothing useful for inline data and can misbehave in iframes.
html = html.replace(' loading="lazy"', "")

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024 / 1024:.1f} MB)")
