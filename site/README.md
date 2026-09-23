# Facility Improvements page (EIS parent portal)

Production build of `project/Facility Improvements v4.dc.html`: plain HTML/CSS, no JavaScript.

- `index.html` – the page; photos load from `images/`.
- `images/` – the 14 photos from the design (extracted from `project/.image-slots.state.json`), plus the Library "before" photo and the Head of School portrait (cropped to 380:440 and brightened) added later.
- `../scripts/build_embed.py` – builds `dist/facility-improvements-embed.html`, a single file with every photo inlined, for pasting into Google Sites → Insert → Embed → Embed code.

```sh
python3 scripts/build_embed.py
```
