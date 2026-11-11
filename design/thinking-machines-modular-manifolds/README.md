# Thinking Machines — blog post design language

A reusable extraction of the design used by
[thinkingmachines.ai/blog/modular-manifolds](https://thinkingmachines.ai/blog/modular-manifolds/),
packaged so any text can be dropped into the same element structure and rendered
with the same look.

It is an academic-paper aesthetic turned into a web essay: warm white paper, a
book serif for prose, quiet grotesque for every piece of UI, one 660 px reading
column in the middle of a three-column grid, marginalia instead of tooltips, and
almost no boxes — depth comes from hairlines and a single `#F3F3F2` code surface.

```
.
├── tokens.json            machine-readable config: colours, type, layout, motion
├── tokens.css             the same tokens as CSS custom properties (+ @font-face)
├── theme.css              layout + all components (load after tokens.css)
├── template.html          the page shell, with {{slots}}
├── build.py               fills the slots from structured content
├── content.example.json   this article's text, typed into blocks
├── index.html             the rendered result (open this first)
├── styleguide.html        the design language demonstrated in itself: type,
│                          colour, tables, figures, code, components, layout
├── extract_content.py     re-extracts text from source/page.html
├── source/                raw evidence: the page HTML and its CSS
└── assets/
    ├── fonts/             Iowan Old Style, GT America, Chakra Petch (woff2)
    └── img/               cover + static figures (svg)
```

---

## 1. How to put your own text in it

The design is **tokens + stylesheet**. The content is **JSON**. Nothing about the
look lives in the text, and nothing about the text lives in the CSS.

**Option A — structured content (recommended).** Edit `content.example.json`
(keep the shape) and rebuild:

```bash
python3 build.py                                   # -> index.html
python3 build.py --content my-essay.json --out my-essay.html
```

`content.example.json`:

```json
{
  "meta": { "title": "...", "subtitle": "", "author": "...", "authorUrl": "...",
            "date": "...", "description": "...", "cover": "assets/img/cover.svg",
            "prev": {"label": "", "href": ""}, "next": {"label": "", "href": ""} },
  "toc": [ { "id": "introduction", "label": "Introduction" } ],
  "blocks": [
    { "type": "heading",   "level": 2, "id": "introduction", "text": "Introduction" },
    { "type": "paragraph", "html": "Inline <em>HTML</em> plus math $x^2$ and <a href=\"#\">links</a>." },
    { "type": "math",      "tex": "\\mathcal{L}(a,\\lambda)=a^\\top g+\\tfrac{\\lambda}{2}(a^\\top a-\\eta)" },
    { "type": "list",      "ordered": false, "html": ["<strong>Bold lead.</strong> Rest of the item."] },
    { "type": "figure",    "id": "fig:one", "caption": "Caption text.",
      "media": { "type": "image", "src": "assets/img/one.svg", "alt": "" } },
    { "type": "table",     "html": "<table>...</table>" },
    { "type": "code",      "language": "python", "code": "print('hi')" }
  ]
}
```

Blocks become exactly the markup `theme.css` expects (see §6). Figures are
numbered automatically and captions get the `Figure N:` prefix; in-text
references are plain anchors to the figure id.

**Look at `styleguide.html`** for a live specimen of every element and value
described below — it is built from the same two stylesheets.

**Option B — hand-written HTML.** Copy the structure from `index.html` /
`template.html` and fill elements directly. The contract is one attribute:
every text node carries `class="typography" data-typography="article-body"`
(headings use `article-heading`, the title `article-title`). That is how the
original page tags its text too.

Two rules that keep the design intact:

1. Never widen the reading column. Everything else can change.
2. Prose is serif, chrome is sans. Don't set a paragraph in GT America.

---

## 2. Colour

The palette is 95 % grayscale. Accent colour appears only inside figures,
syntax highlighting and KaTeX.

| token | value | use |
|---|---|---|
| `--bg` | `#FFFFFF` | page |
| `--bg_code` | `#F3F3F2` | code blocks (the only filled surface) |
| `--fg` | `#282828` | body text, active TOC, headings |
| `--fg1` | `#3C3836` | nav links, footer links |
| `--fg2` | `#504945` | blockquotes, hover links |
| `--fg3` | `#6B6866` | captions, table headers, byline date |
| `--fg4` | `#676767` | default link / TOC / muted text |
| `--fg5` | `#969696` | disabled, epigraph rule |
| `--rule-table` | `#D9D9D9` | table row rules |
| footer rule | `rgba(103,103,103,.1)` | hairline above footer |
| link underline | `rgba(103,103,103,.3)` | prose links |
| selection | `rgba(0,0,0,.12)` | |

Brand accents (`--brand-cobalt #0155BF`, `--brand-azure #0387E7`,
`--brand-emerald #0E9972`, `--brand-lime #9CC355`, `--brand-yellow #FFCE52`,
`--brand-amber #F7A224`, `--brand-red #EF402C`) exist in the tokens but are not
used in article chrome. Syntax colours live in `theme.css` (`--code-*`) and in
the original `source/syntax.css`.

There are **no shadows, no gradients, no cards, no coloured backgrounds** in the
reading experience. The only radii are the code block (7 px) and the video
radius (12 px).

---

## 3. Typography

| role | family | size | weight | line-height |
|---|---|---|---|---|
| article title | Iowan Old Style | 30 px (`1.875rem`) | 600 | 1.4 |
| subtitle | Iowan Old Style italic | 24 px | 400 | 1.5 |
| h2 | Iowan Old Style | 23.2 px (`1.45rem`) | 600 | 1.4 |
| h3 | Iowan Old Style italic | 21.6 px (`1.35rem`) | 400 | 1.4 |
| h4 | Iowan Old Style italic | 15.5 px (`0.97rem`) | 400 | 1.4 |
| body | Iowan Old Style | **17 px** (`1.0625rem`) | 400 | **1.6** |
| byline / date | GT America | 15 px | 400, `+0.24px` | 17 / 21 px |
| nav | GT America | 15 px | 400, `-0.01em` | 1.3 |
| captions, TOC, tables | GT America | 13 px | 400 | 1.4–1.5 |
| footer | GT America | 15 px | 400 | 1.5 |
| logo | Chakra Petch | 17 px | 500, `+1.7px` | 25 px |
| inline code | GT America Mono | 0.9 em | 400 | — |
| code block | GT America Mono | 13 px | 400 | 1.4 |

Notes:

- **Iowan Old Style** is the whole voice of the page. It is a transitional
  book face with sharp serifs; at 17/1.6 it reads like a printed essay, not a
  blog. Fallback `Georgia, serif`.
- **GT America** carries all metadata. The contrast between the two is the
  signature of the design: reading text = serif, apparatus = sans.
- **Chakra Petch** appears once, on `THINKING MACHINES`, with wide tracking.
- Headings are sentence case, never all-caps, and never letter-spaced.
- h3/h4 are *italic*, not bold. Bold is reserved for `strong` and table headers.
- Math is KaTeX at `font-size: 100%`, so inline symbols match the serif x-height.

---

## 4. Layout

```
┌──────────────────────────────────────────────────────────────┐
│ fixed header, 54px, white, logo left / nav right             │
├──────────────────────────────────────────────────────────────┤
│                  title (max 710, centred)                    │
│                  author · date                               │
│                  cover (max 800)                             │
│                                                              │
│  ┌────────────┐   ┌──────────────────────┐   ┌───────────┐   │
│  │ left TOC   │   │  article 660px       │   │ sidenotes │   │
│  │ 210 + 34   │   │  (grid column 2)     │   │ 230–300   │   │
│  └────────────┘   └──────────────────────┘   └───────────┘   │
│                                                              │
│                    prev · back to top · next                 │
│  ─────────────────────────────────────────────────────────   │
│  footer, 5 columns, max 952px                                │
└──────────────────────────────────────────────────────────────┘
```

- Shell: `grid-template-columns: minmax(0,1fr) minmax(0,660px) minmax(0,1fr)`.
  The middle track is the only thing text may occupy.
- Shell max width grows with the viewport so the rails get room, while the text
  stays 660: `950 → 970 (≥1200) → 990 (≥1400) → 1010 (≥1600) → 1030 (≥1800)`.
- The TOC is `position: sticky; top: 2rem`, right-aligned, 210 px + 1.3 rem
  gutter, and hidden below 1280 px (article then centres).
- Sidenotes float right into the margin rail: width 230 px (240/250/275/300 at
  the same breakpoints), 64 px gap, negative right margin.
- Header is fixed and hides on scroll-down (`translateY(-100%)`), 54 px
  (50 px mobile). Nav appears at ≥641 px, hamburger below.
- Footer: 5 columns above 800 px, 2 below; max 952 px; 9 rem of air above.
- Page padding: 1 rem, dropping to `1.3rem` content padding for the article body.

Vertical rhythm:

| gap | value |
|---|---|
| paragraph → paragraph | `1.45rem` |
| h2 top / bottom | `3.1rem` / `1.2rem` |
| h3 top / bottom | `2.8rem` / `1.05rem` |
| h4 top / bottom | `2.2rem` / `0.8rem` |
| list top / bottom | `1rem` / `1.2rem` |
| figure margins | `1.8rem` + `0.75rem` block padding |
| figure → caption | `13px` |
| display math | `1.2rem + 0.45rem` |
| code block | `1.2rem + 0.2rem` |
| footer above | `9rem` |

The rhythm is asymmetric on purpose: space above a heading is much larger than
below it, so headings belong to the text that follows.

---

## 5. Components

- **Prose links** — `#676767` with a 30 %-opacity underline; hover darkens the
  ink to `#504945` and the underline to 30 % of that. No bold, no colour.
- **Heading anchor** — a serif `#` sits 1.2 rem left of h2–h6 at 0 opacity,
  revealed on hover. Never visible at rest.
- **Blockquote** — 2 px left rule at 35 % gray, ink `#504945`, 1 rem inset,
  1.25 rem padding. Epigraph variant: 3 px rule at 60 % `#969696`, italic 1.05 rem.
- **Lists** — `square` bullets for `ul`, decimal for `ol` (lower-alpha nested),
  0.2 rem between items, 1.5/2 rem indent.
- **Table** — the essay table is *not* a grid: no vertical rules, no header fill,
  header text in 13 px `#6B6866` regular, each row closed by a 1 px `#D9D9D9`
  rule, `0.78rem 1.25rem` padding. (The generic grid style remains available for
  data tables.)
- **Inline code** — mono at 0.9 em, `#AD2111`, no background.
- **Code block** — `#F3F3F2`, 7 px radius, 13 px mono `#6B6866`, 1.25 rem
  padding (2 rem right), optional 11 px sans language chip top-left.
- **Figure** — image max 800 px, left-aligned caption in 13 px sans `#6B6866`,
  13 px below the image, prefix `Figure N: ` in 500 weight. No frame, no shadow.
- **Sidenote / marginnote** — superscript number in `#676767`, note floated into
  the right rail at 0.9 rem/1.4. Below 768 px the note collapses and opens on
  tap (checkbox `.margin-toggle`).
- **TOC** — 13 px sans, `#676767`; active item `#282828` plus a 4 px dot in the
  gutter that slides between items with a 0.28 s quintic ease.
- **Paginator** — three equal columns: `prev` · `back to top` · `next`, all
  lowercase, 15 px sans.
- **Footer** — 15 px sans, headings `#676767`, links `#3C3836`, hairline rule
  above, `Thinking Machines Lab © 2026` 3 rem under the columns.

---

## 6. Element / class contract

If you write HTML by hand, this is the whole vocabulary `theme.css` needs.

```html
<div id="wrapper">
  <header id="header"> <div class="site-header">
    <div class="navbar-logo"><a href="/">THINKING MACHINES</a></div>
    <nav class="top-nav">
      <a href="…"><span class="typography" data-typography="body-legacy">…</span></a>
    </nav>
  </div></header>

  <main id="main" class="post">
    <div class="post-heading">
      <h1 class="typography post-title" data-typography="article-title">Title</h1>
      <p class="typography post-subtitle">Optional dek</p>
      <div class="publish-metadata">
        <span class="author"><a href="…">Author</a></span><span>Date</span>
      </div>
    </div>
    <div class="post-cover"><img class="cover-image" src="…" alt=""></div>

    <div class="post-content-shell">
      <nav id="left-toc" class="left-toc"><ul class="toc-list">
        <li class="toc-item"><a href="#id">Section</a></li>
      </ul></nav>

      <article class="content">
        <p class="typography" data-typography="article-body">Prose…</p>
        <h2 id="id" class="typography" data-typography="article-heading">Section</h2>
        <figure id="fig:x">
          <img class="figure-media" src="…" alt="">
          <figcaption>Caption.</figcaption>
        </figure>
      </article>
    </div>

    <div class="paginator"> <a>prev</a> <a href="#top">back to top</a> <a>next</a> </div>
  </main>

  <footer id="footer"> … </footer>
</div>
```

Typography presets: `article-title`, `article-heading`, `article-subheading`,
`article-body`, `body-legacy`, `body-large`.

---

## 7. Motion

| what | timing |
|---|---|
| page enter | `fadeIn .6s ease-in-out` |
| links | `color .3s, text-decoration-color .3s` |
| header hide / show | `transform .22s cubic-bezier(.22,1,.36,1)` |
| TOC item | `color .2s, opacity .2s` |
| TOC dot | `transform .28s cubic-bezier(.22,1,.36,1)` |
| heading anchor | `opacity .15s` |

Everything is disabled under `prefers-reduced-motion: reduce`. There are no
parallax effects, no scroll-triggered reveals, no entrance animations per block.

---

## 8. Fidelity notes

- **Fonts are proprietary.** Iowan Old Style (Apple), GT America (Grilli Type)
  and Chakra Petch (Cadson Demak) are included in `assets/fonts` so the local
  preview looks right. Swap in licensed copies, or let the stacks fall back to
  Georgia / system sans, for anything you publish.
- **Interactive figures.** The original has four Three.js canvases (tangent
  space, norm balls, gradient, retraction). They are represented here by
  captioned placeholders (`media.type = "placeholder"`) because they are scripts,
  not design. Static figures (SVD, CIFAR-10, product manifold) are included as SVG.
- **Math** is rendered client-side by KaTeX from a CDN in `template.html`; the
  original bundles KaTeX locally. Formulas are stored as raw TeX in
  `content.example.json`.
- **Table styling** is taken from what the live page actually renders
  (borderless rows, hairline rules); the generic table CSS in the source is a
  grid variant that this post does not use.
- The original page also ships a mobile menu, scroll-spy for the TOC, a
  scroll-hiding header, and a copy button on code blocks. A compact scroll-spy
  and mobile menu are included; the rest is omitted.

## 9. Source

Captured 2026-11-10 from
`https://thinkingmachines.ai/blog/modular-manifolds/`:
`source/page.html` (snapshot), `source/blog-post.css` and `source/syntax.css`
(the two stylesheets the page loads). All numbers in `tokens.json` were read
from those files, not eyeballed.
