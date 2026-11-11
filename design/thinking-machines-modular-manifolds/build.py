#!/usr/bin/env python3
"""
Render a Thinking Machines-style essay from structured text.

    python3 build.py                          # content.example.json -> index.html
    python3 build.py --content my-text.json --out my-essay.html

The design is defined by tokens.css + theme.css; the template.html file holds
the page shell with {{slots}}; this script only fills those slots and turns the
content blocks into the markup the stylesheet expects.
"""

import argparse
import html as ht
import json
from pathlib import Path

ROOT = Path(__file__).parent

NAV = [
    ("Inkling", "/inkling/"),
    ("Tinker", "/tinker/"),
    ("Connectionism", "/blog/"),
    ("News", "/news/"),
    ("Join us", "/#join-us"),
]


# ------------------------------------------------------------------ blocks --
def render_blocks(blocks):
    out = []
    for b in blocks:
        kind = b["type"]

        if kind == "heading":
            level = b.get("level", 2)
            anchor = f'<a class="heading-anchor" href="#{b["id"]}" aria-hidden="true">#</a>' if b.get("id") else ""
            typo = "article-heading" if level == 2 else "article-subheading"
            out.append(
                f'<h{level} id="{b.get("id") or ""}" class="typography" data-typography="{typo}">'
                f'{b["text"]}{anchor}</h{level}>'
            )

        elif kind == "paragraph":
            out.append(f'<p class="typography" data-typography="article-body">{b["html"]}</p>')

        elif kind == "math":
            out.append(f'<div class="math-display">$$\n{b["tex"]}\n$$</div>')

        elif kind == "list":
            tag = "ol" if b.get("ordered") else "ul"
            items = "".join(
                f'<li class="typography" data-typography="article-body">{item}</li>'
                for item in b["html"]
            )
            out.append(f'<{tag} class="typography">{items}</{tag}>')

        elif kind == "figure":
            media = b["media"]
            if media.get("type") == "image":
                body = (
                    f'<img class="figure-media" src="{media["src"]}" alt="{media.get("alt", "")}" loading="lazy">'
                )
            else:
                label = media.get("label", "figure")
                aspect = media.get("aspect", "3 / 2")
                body = (
                    f'<div class="figure-media" role="img" aria-label="{label}" '
                    f'style="aspect-ratio:{aspect};background:var(--bg_code);'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font:400 13px/1.4 var(--font-sans);color:var(--fg5);letter-spacing:.02em">'
                    f'{label}</div>'
                )
            fig_id = f' id="{b["id"]}"' if b.get("id") else ""
            cap = f'<figcaption>{b["caption"]}</figcaption>' if b.get("caption") else ""
            out.append(f"<figure{fig_id}>{body}{cap}</figure>")

        elif kind == "table":
            out.append(b["html"])

        elif kind == "code":
            code = ht.escape(b["code"])
            lang = b.get("language", "text")
            attr = "" if lang in ("text", "plaintext") else f' data-lang="{lang}"'
            out.append(f'<pre><code{attr}>{code}</code></pre>')

        elif kind == "html":
            out.append(b["html"])

    return "\n".join(out)


def render_toc(toc):
    return "".join(
        f'<li class="toc-item"><a href="#{item["id"]}">{item["label"]}</a></li>' for item in toc
    )


# ------------------------------------------------------------------- page ---
def build(content, template):
    meta = content["meta"]

    subtitle = (
        f'<p class="typography post-subtitle">{meta["subtitle"]}</p>' if meta.get("subtitle") else ""
    )

    author = meta.get("author", "")
    if author:
        author_link = (
            f'<a href="{meta["authorUrl"]}" rel="me noopener" target="_blank">{author}</a>'
            if meta.get("authorUrl")
            else author
        )
    else:
        author_link = ""

    cover = (
        f'<div class="post-cover"><img class="cover-image" src="{meta["cover"]}" alt=""></div>'
        if meta.get("cover")
        else ""
    )

    nav_links = "".join(
        f'<a href="{href}"><span class="typography" data-typography="body-legacy">{label}</span></a>'
        for label, href in NAV
    )
    mobile_links = "".join(
        f'<a href="{href}"><span class="typography" data-typography="body-large">{label}</span></a>'
        for label, href in NAV
    )

    prev = meta.get("prev") or {}
    nxt = meta.get("next") or {}
    prev_link = f'<a href="{prev["href"]}">{prev["label"]}</a>' if prev.get("href") else "<a>prev</a>"
    next_link = f'<a href="{nxt["href"]}">{nxt["label"]}</a>' if nxt.get("href") else "<a>next</a>"

    slots = {
        "title": meta.get("title", ""),
        "description": meta.get("description", ""),
        "author": author,
        "date": meta.get("date", ""),
        "author_link": author_link,
        "subtitle": subtitle,
        "cover": cover,
        "nav_links": nav_links,
        "mobile_links": mobile_links,
        "toc": render_toc(content.get("toc", [])),
        "body": render_blocks(content["blocks"]),
        "prev_link": prev_link,
        "next_link": next_link,
    }

    page = template
    for key, value in slots.items():
        page = page.replace("{{" + key + "}}", value)
    return page


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", default="content.example.json")
    ap.add_argument("--template", default="template.html")
    ap.add_argument("--out", default="index.html")
    args = ap.parse_args()

    content = json.loads((ROOT / args.content).read_text())
    template = (ROOT / args.template).read_text()
    (ROOT / args.out).write_text(build(content, template))
    print(f"wrote {args.out} from {args.content}")


if __name__ == "__main__":
    main()
