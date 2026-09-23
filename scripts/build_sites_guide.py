#!/usr/bin/env python3
"""Build a step-by-step guide for recreating site/index.html with native
Google Sites blocks (text boxes, images, layouts), which reflow on phones.

Text is pulled straight from site/index.html so the guide never drifts from
the page. Usage: build_sites_guide.py OUT_HTML
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
PHOTO_URL = "https://b69s.github.io/eis-facility/photos/"
ZIP_URL = "https://b69s.github.io/eis-facility/eis-facility-photos.zip"
PHOTOS = {
    "head-portrait": "00-head-of-school", "reception-before": "01-reception-before",
    "reception-after": "02-reception-after", "hub-after": "03-community-hub",
    "lounge-before": "04-student-lounge-before", "lounge-after": "05-student-lounge-after",
    "library-before": "06-library-before", "library-after": "07-library-after",
    "paint-before": "08-painting-before", "paint-after": "09-painting-after",
    "doors-after": "10-classroom-doors", "floor-before": "11-flooring-before",
    "floor-after": "12-flooring-after", "arts-after": "13-visual-arts-room",
    "music-after": "14-music-instruments", "couns-after": "15-counsellor-room",
}


def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def section(sid):
    return re.search(rf'<section id="{sid}">(.*?)</section>', PAGE, re.S).group(1)


def first(pattern, s):
    m = re.search(pattern, s, re.S)
    return text(m.group(1)) if m else ""


def chunk(label, lines):
    """lines: list of (style, text); style in title|heading|sub|small|p."""
    tags = {"title": "h1", "heading": "h2", "sub": "h3", "small": "p", "p": "p"}
    rich = "".join(
        f"<{tags[k]}>{'<b>' + html.escape(t) + '</b>' if k == 'small' else html.escape(t)}</{tags[k]}>"
        for k, t in lines if t)
    plain = "\n\n".join(t for _, t in lines if t)
    return {"label": label, "lines": [[k, t] for k, t in lines if t], "html": rich, "plain": plain}


def photo(slot):
    name = PHOTOS[slot]
    return {"name": name, "url": PHOTO_URL + name + ".jpg", "file": f"photos/{name}.jpg"}


sections = []

# 1. Header + numbers
hdr = re.search(r"<header>(.*?)</header>", PAGE, re.S).group(1)
stats = re.findall(r'stat-num">(.*?)<.*?stat-label">(.*?)<.*?stat-jp">(.*?)<', hdr, re.S)
sections.append({
    "title": "Заголовок и цифры",
    "steps": [
        "Вставьте текстовый блок (двойной клик по пустому месту → значок «T»). Вставьте блок «Заголовок». Строку «A better campus for every student» сделайте стилем <b>Title</b>.",
        "Ниже вставьте ещё два текстовых блока рядом: английский текст слева, японский справа. Второй блок перетащите вправо от первого, Google Sites сам поставит их в две колонки.",
        "Для цифр создайте новую секцию: наведите на неё, слева нажмите значок палитры <b>Section background</b> → <b>Emphasis 2</b> (самый насыщенный цвет темы). В ней три текстовых блока рядом, по одному на цифру; цифру сделайте стилем <b>Title</b>.",
    ],
    "chunks": [
        chunk("Заголовок", [("small", first(r'class="eyebrow">(.*?)<', hdr)), ("title", first(r"<h1>(.*?)</h1>", hdr)), ("sub", first(r'class="h1-jp">(.*?)<', hdr))]),
        chunk("Вступление (EN)", [("p", first(r'<p class="en">(.*?)</p>', hdr))]),
        chunk("Вступление (JA)", [("p", first(r'<p class="jp">(.*?)</p>', hdr))]),
    ] + [chunk(f"Цифра {n}", [("title", n), ("small", l), ("p", jp)]) for n, l, jp in stats],
    "photos": [],
})

# 2. Message
msg = section("message")
paras = [text(p) for p in re.findall(r"<p>(.*?)</p>", msg, re.S)]
sections.append({
    "title": "Обращение директора",
    "steps": [
        "<b>Insert → Layouts</b> → макет «фото слева, текст справа».",
        "Кликните по месту для фото → <b>Select image → By URL</b> → вставьте ссылку на портрет. Под фото в тексте макета: «Head of School / Enishi International School».",
        "В текстовую часть вставьте блок «Обращение». Цитату сделайте стилем <b>Heading</b>.",
    ],
    "chunks": [chunk("Обращение", [("small", first(r'class="eyebrow">(.*?)<', msg) + " ・ " + first(r'class="sub-jp">(.*?)<', msg)), ("heading", first(r"<blockquote>(.*?)</blockquote>", msg))] + [("p", p) for p in paras]),
               chunk("Подпись под фото", [("sub", "Head of School"), ("p", "Enishi International School")])],
    "photos": [photo("head-portrait")],
})

# 3–5. Completed, split by group
comp = section("completed")
groups = re.split(r'(?=<div class="group-head)', comp)
intro = groups[0]
PAIR_STEPS = "С двумя фото «до / после»: <b>Insert → Layouts</b> → макет с двумя фото рядом. Слева «до», справа «после». Чтобы подписать фото, кликните по нему → ⋮ → <b>Add caption</b>, напишите «Before» или «After». Название и описание вставьте в текстовые поля макета или отдельным текстовым блоком под фото."
SINGLE_STEPS = "С одним фото: <b>Insert → Layouts</b> → «фото слева, текст справа», у следующего такого проекта для разнообразия — «текст слева, фото справа»."
CARD_STEPS = "Проекты без фото: текстовые блоки по три в ряд (вставьте блок и перетащите его рядом с предыдущим). Название — стилем <b>Subheading</b>."
for gi, g in enumerate(groups[1:], 1):
    num, gname, gjp = re.search(r'class="num">(.*?)<.*?<h3>(.*?)</h3>.*?class="jp">(.*?)<', g, re.S).groups()
    chunks, photos = [], []
    if gi == 1:
        chunks.append(chunk("Заголовок раздела «Completed»", [("small", first(r'class="eyebrow">(.*?)<', intro)), ("title", first(r'<h2 class="big">(.*?)</h2>', intro)), ("p", first(r'class="lede">(.*?)</p>', intro))]))
    chunks.append(chunk(f"Группа {num}", [("heading", text(gname)), ("p", text(gjp))]))
    for art in re.findall(r"<article.*?</article>", g, re.S):
        slots = re.findall(r'src="images/(.*?)\.webp"', art)
        photos += [photo(s) for s in slots]
        kind = "до / после" if len(slots) == 2 else "одно фото"
        chunks.append(chunk(f"{first(r'<h4>(.*?)</h4>', art)} ({kind})", [("sub", first(r"<h4>(.*?)</h4>", art)), ("p", first(r"<p>(.*?)</p>", art)), ("small", first(r'class="badge">(.*?)<', art))]))
    for card in g.split('<div class="card">')[1:]:
        chunks.append(chunk(first(r"<h4>(.*?)</h4>", card), [("small", first(r'class="tag">(.*?)<', card)), ("sub", first(r"<h4>(.*?)</h4>", card)), ("p", first(r"<p>(.*?)</p>", card))]))
    sections.append({"group": gi, "title": f"Выполнено · {text(gname)}", "chunks": chunks, "photos": photos})

# Merge completed groups 3–5 into one guide step to keep the list short.
done = [s for s in sections if "group" in s]
merged = [done[0], done[1], {"title": "Выполнено · Специальные кабинеты, благополучие, комфорт", "chunks": sum((s["chunks"] for s in done[2:]), []), "photos": sum((s["photos"] for s in done[2:]), [])}]
sections = [s for s in sections if "group" not in s] + merged
for s in merged:
    s["steps"] = ([] if s is not merged[0] else ["Каждую группу начинайте с текстового блока с заголовком группы (стиль <b>Heading</b>)."]) + [PAIR_STEPS, SINGLE_STEPS, CARD_STEPS]
    if s is merged[0]:
        s["steps"].insert(0, "Начните новую секцию. Вставьте блок «Заголовок раздела», строку «Twenty projects, finished» сделайте стилем <b>Title</b>.")

# 6. Why it matters
lrn = section("learning")
sections.append({
    "title": "Почему это важно",
    "steps": ["Новая секция с фоном <b>Emphasis 1</b> (светлый оттенок темы).", "Текстовый блок с заголовком, затем шесть текстовых блоков по три в ряд."],
    "chunks": [chunk("Заголовок", [("small", first(r'class="eyebrow">(.*?)<', lrn)), ("heading", first(r"<h2[^>]*>(.*?)</h2>", lrn)), ("p", first(r'class="lede">(.*?)</p>', lrn))])]
    + [chunk(text(h), [("sub", text(h)), ("p", text(p))]) for h, p in re.findall(r'<div class="reason">.*?<h3>(.*?)</h3>\s*<p>(.*?)</p>', lrn, re.S)],
    "photos": [],
})

# 7. In progress
prg = section("progress")
sections.append({
    "title": "В процессе",
    "steps": ["Обычная белая секция. Текстовый блок с заголовком, затем десять текстовых блоков по три в ряд.", "Совет для телефона: вместо десяти блоков можно использовать <b>Insert → Collapsible text</b>, тогда на телефоне будет виден только список названий, а текст раскрывается по нажатию."],
    "chunks": [chunk("Заголовок", [("small", first(r'class="eyebrow">(.*?)<', prg)), ("heading", first(r"<h2[^>]*>(.*?)</h2>", prg))])]
    + [chunk(text(h), [("small", text(t)), ("sub", text(h)), ("p", text(p))]) for t, h, p in re.findall(r'class="pill[^"]*">(.*?)</div>\s*<h4>(.*?)</h4>\s*<p>(.*?)</p>', prg, re.S)],
    "photos": [],
})

# 8. Future + contact
fut = section("future")
foot = re.search(r"<footer>(.*?)</footer>", PAGE, re.S).group(1)
sections.append({
    "title": "Планы и контакты",
    "steps": ["Новая секция с фоном <b>Emphasis 2</b>. Заголовок, затем шесть текстовых блоков по три в ряд.", "Последняя секция: текстовый блок «Контакты», рядом <b>Insert → Button</b>: название <code>office@enishi.ac.jp</code>, ссылка <code>mailto:office@enishi.ac.jp</code>."],
    "chunks": [chunk("Заголовок", [("small", first(r'class="eyebrow">(.*?)<', fut)), ("heading", first(r"<h2[^>]*>(.*?)</h2>", fut)), ("p", first(r'class="lede">(.*?)</p>', fut))])]
    + [chunk(text(h), [("small", text(w)), ("sub", text(h)), ("p", text(p))]) for w, h, p in re.findall(r'class="when">(.*?)</div>\s*<h4>(.*?)</h4>\s*<p>(.*?)</p>', fut, re.S)]
    + [chunk("Контакты", [("heading", first(r"<h2>(.*?)</h2>", foot))] + [("p", text(p)) for p in re.findall(r"<p[^>]*>(.*?)</p>", foot, re.S)] + [("p", "office@enishi.ac.jp"), ("p", first(r'class="tel">(.*?)<', foot))])],
    "photos": [],
})

Path(sys.argv[1]).write_text(
    (Path(__file__).parent / "sites_guide_template.html").read_text(encoding="utf-8")
    .replace("__DATA__", json.dumps({"sections": sections, "zip": ZIP_URL}, ensure_ascii=False).replace("</", "<\\/")),
    encoding="utf-8")
print(len(sections), "sections,", sum(len(s["chunks"]) for s in sections), "text blocks,", sum(len(s["photos"]) for s in sections), "photos")
