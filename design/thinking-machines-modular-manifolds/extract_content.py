#!/usr/bin/env python3
"""
Extract the text content of the source page into structured JSON.

Input : source/page.html          (raw snapshot of the live page)
Output: content.example.json      (meta + toc + typed content blocks)

Each block is a plain data record. The renderer in build.py turns it into the
markup that theme.css expects, so swapping the text = swapping the JSON.

Block types produced:
  heading   {level, id, text}
  paragraph {html}                 inline html, math kept as $...$
  math      {tex}                  display equation
  list      {ordered, html}        <li> items with inline html
  figure    {id, caption, media}   media = {type: image|placeholder, ...}
  table     {html}
  code      {language, code}
"""

import html as ht
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "source" / "page.html"
OUT = ROOT / "content.example.json"

VOID = {
    "br", "img", "input", "hr", "meta", "link", "source",
    "path", "circle", "rect", "line", "use", "stop", "ellipse", "polygon",
}

# ---------------------------------------------------------------- katex ----
SPAN_TOK = re.compile(r"<span\b|</span>")


def katex_to_tex(src: str) -> str:
    """Replace every KaTeX span tree with $tex$ / $$tex$$."""
    out, pos = [], 0
    opener = re.compile(r'<span class="katex(-display)?">')
    while True:
        m = opener.search(src, pos)
        if not m:
            out.append(src[pos:])
            break
        start = m.start()
        out.append(src[pos:start])
        depth, k = 0, start
        while True:
            t = SPAN_TOK.search(src, k)
            if not t:
                end = len(src)
                break
            depth += -1 if t.group(0).startswith("</") else 1
            k = t.end()
            if depth == 0:
                end = k
                break
        block = src[start:end]
        ann = re.search(
            r'<annotation encoding="application/x-tex">(.*?)</annotation>',
            block,
            re.S,
        )
        tex = ht.unescape(ann.group(1)).strip() if ann else ""
        if m.group(1):  # katex-display
            out.append(f'<span class="math-display">{tex}</span>')
        else:
            out.append(f'<span class="math-inline">${tex}$</span>')
        pos = end
    return "".join(out)


# ---------------------------------------------------------- block split ----
TAG = re.compile(r"<(/?)([a-zA-Z0-9:-]+)([^>]*?)(/?)>", re.S)


def split_top_level(fragment: str):
    """Yield top-level element chunks, in document order."""
    chunks, stack, start = [], [], None
    for m in TAG.finditer(fragment):
        closing, tag, _attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if start is None:
            start = m.start()
        if tag in VOID or selfclose:
            continue
        if closing:
            if stack and stack[-1] == tag:
                stack.pop()
            elif tag in stack:
                while stack and stack.pop() != tag:
                    pass
        else:
            stack.append(tag)
        if not stack and start is not None:
            chunks.append(fragment[start:m.end()])
            start = None
    return chunks


# -------------------------------------------------------------- cleaning ----
def clean(html: str) -> str:
    html = re.sub(r'\s*data-astro-cid-[a-z0-9]+="[^"]*"', "", html)
    html = re.sub(r'\s*data-typography="[^"]*"', "", html)
    html = re.sub(r'\s*class="typography"', "", html)
    html = re.sub(r'\s*data-zoomable="[^"]*"', "", html)
    html = re.sub(r'\s*tabindex="[^"]*"', "", html)
    html = re.sub(r'\s*style="[^"]*"', "", html)
    html = re.sub(r"\s+>", ">", html)
    return html.strip()


def parse_figure(chunk: str):
    fig_id = re.search(r'<figure[^>]*id="([^"]*)"', chunk)
    cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", chunk, re.S)
    img = re.search(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"', chunk)
    media = None
    if img:
        src = img.group(1).replace("svgs/", "assets/img/")
        media = {"type": "image", "src": src, "alt": img.group(2)}
    else:
        media = {
            "type": "placeholder",
            "label": "interactive canvas",
            "aspect": "3 / 2",
        }
    return {
        "type": "figure",
        "id": fig_id.group(1) if fig_id else None,
        "caption": clean(cap.group(1)) if cap else "",
        "media": media,
    }


def parse_blocks(fragment: str):
    blocks = []
    for chunk in split_top_level(fragment):
        tag = re.match(r"<([a-zA-Z0-9]+)", chunk).group(1).lower()
        if tag in ("script", "style"):
            continue

        if tag == "h2":
            hid = re.search(r'id="([^"]*)"', chunk)
            text = clean(re.sub(r"<[^>]+>", "", chunk))
            blocks.append({"type": "heading", "level": 2, "id": hid.group(1) if hid else None, "text": text})
        elif tag == "h3":
            hid = re.search(r'id="([^"]*)"', chunk)
            text = clean(re.sub(r"<[^>]+>", "", chunk))
            blocks.append({"type": "heading", "level": 3, "id": hid.group(1) if hid else None, "text": text})
        elif tag == "p":
            inner = clean(re.sub(r"^<p[^>]*>|</p>$", "", chunk, flags=re.S).strip())
            display = re.fullmatch(r'<span class="math-display">(.*?)</span>', inner, re.S)
            if display:
                blocks.append({"type": "math", "tex": display.group(1)})
            else:
                blocks.append({"type": "paragraph", "html": inner})
        elif tag in ("ul", "ol"):
            items = [clean(i) for i in re.findall(r"<li[^>]*>(.*?)</li>", chunk, re.S)]
            blocks.append({"type": "list", "ordered": tag == "ol", "html": items})
        elif tag == "span" and chunk.startswith('<span class="math-display">'):
            inner = re.sub(r'^<span class="math-display">|</span>$', "", chunk, flags=re.S)
            blocks.append({"type": "math", "tex": inner})
        elif tag == "figure":
            blocks.append(parse_figure(chunk))
        elif tag == "table":
            blocks.append({"type": "table", "html": clean(chunk)})
        elif tag == "pre":
            lang = re.search(r'data-language="([^"]*)"', chunk)
            code_html = re.search(r"<code[^>]*>(.*?)</code>", chunk, re.S)
            raw = code_html.group(1) if code_html else ""
            lines = re.split(r'<span class="line">', raw)[1:] or [raw]
            code = "\n".join(
                ht.unescape(re.sub(r"<[^>]+>", "", ln)).rstrip("\n") for ln in lines
            )
            blocks.append(
                {"type": "code", "language": lang.group(1) if lang else "text", "code": code.rstrip("\n")}
            )
        else:
            blocks.append({"type": "html", "html": clean(chunk)})
    return blocks


# ------------------------------------------------------------------ main ----
def main() -> None:
    page = SRC.read_text()

    title = re.search(r'<h1[^>]*class="[^"]*post-title[^"]*"[^>]*>(.*?)</h1>', page, re.S)
    subtitle = re.search(r'<p[^>]*class="[^"]*post-subtitle[^"]*"[^>]*>(.*?)</p>', page, re.S)
    author = re.search(
        r'<span class="author">\s*<a href="([^"]*)"[^>]*>(.*?)</a>', page, re.S
    )
    date = re.search(r'<span class="author">.*?</span>\s*<span>(.*?)</span>', page, re.S)
    desc = re.search(r'<meta name="description" content="([^"]*)"', page)

    cover = re.search(r'<div class="post-cover">\s*<img src="([^"]*)"', page)

    toc_nav = re.search(r'<nav id="left-toc".*?</nav>', page, re.S)
    toc = []
    if toc_nav:
        for m in re.finditer(r'<a href="#([^"]*)">(.*?)</a>', toc_nav.group(0)):
            toc.append({"id": m.group(1), "label": clean(m.group(2))})

    start = page.find('<article class="content">')
    end = page.find("</article>", start)
    body = page[start + len('<article class="content">') : end]
    body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)

    content = {
        "$comment": "Structured text for the Thinking Machines essay template. Replace strings here, then run build.py.",
        "meta": {
            "title": clean(title.group(1)) if title else "",
            "subtitle": clean(subtitle.group(1)) if subtitle else "",
            "author": clean(author.group(2)) if author else "",
            "authorUrl": author.group(1) if author else "",
            "date": ht.unescape(date.group(1)).strip() if date else "",
            "description": ht.unescape(desc.group(1)) if desc else "",
            "cover": cover.group(1).replace("svgs/", "assets/img/") if cover else "",
            "prev": {"label": "", "href": ""},
            "next": {"label": "", "href": ""},
        },
        "toc": toc,
        "blocks": parse_blocks(katex_to_tex(body)),
    }

    # resolve in-text cross references ("Figure <span data-ref=...>") to numbers
    numbers, order = {}, 0
    for b in content["blocks"]:
        if b["type"] == "figure" and b.get("id"):
            order += 1
            numbers[b["id"].split(":")[-1]] = order

    def fill_refs(text: str) -> str:
        return re.sub(
            r'<span data-ref="([^"]*)"></span>',
            lambda m: str(numbers.get(m.group(1), "")),
            text,
        )

    for b in content["blocks"]:
        for key in ("html", "caption"):
            if isinstance(b.get(key), str):
                b[key] = fill_refs(b[key])
            elif isinstance(b.get(key), list):
                b[key] = [fill_refs(x) for x in b[key]]

    OUT.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.name}: {len(content['blocks'])} blocks, {len(toc)} toc entries")


if __name__ == "__main__":
    main()
